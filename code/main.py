import tkinter as tk
from tkinter import messagebox, filedialog, ttk, colorchooser
import subprocess
import os
import threading
import socket
import time
import re
import shlex
import json

class ToolTip:
    """
    A simple tooltip class for Tkinter widgets.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = 0
        self.y = 0
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        "Display text in tooltip window"
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20 # Offset to the right
        y += self.widget.winfo_rooty() + 20 # Offset downwards

        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True) # Removes window decorations
        self.tip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tip_window, text=self.text, background="#FFFFCC",
                         relief="solid", borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(padx=1)

    def hide_tip(self, event=None):
        "Hide the tooltip window"
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None


class CS2ServerLauncher:
    def __init__(self, master):
        self.master = master
        master.title("CS2 Dedicated Server Launcher")
        master.geometry("850x730")
        master.resizable(False, False)

        self.server_process = None
        self.output_log_thread = None
        self.stop_log_thread = threading.Event()

        # --- Theme Variables and Colors ---
        self.default_light_theme_colors = {
            "bg": "#f0f0f0", "fg": "#333333",
            "frame_bg": "#f0f0f0", "frame_fg": "#333333",
            "entry_bg": "white", "entry_fg": "black",
            "button_bg": "#e1e1e1", "button_fg": "black",
            "active_button_bg": "#c8c8c8", "active_button_fg": "black",
            "log_bg": "#ffffff", "log_fg": "#000000",
            "combobox_bg": "white", "combobox_fg": "black",
            "start_button_bg": "#4CAF50", "stop_button_bg": "#f44336"
        }
        self.default_dark_theme_colors = {
            "bg": "#2e2e2e", "fg": "#e0e0e0",
            "frame_bg": "#3c3c3c", "frame_fg": "#e0e0e0",
            "entry_bg": "#4a4a4a", "entry_fg": "#e0e0e0",
            "button_bg": "#555555", "button_fg": "#ffffff",
            "active_button_bg": "#6a6a6a", "active_button_fg": "#ffffff",
            "log_bg": "#1e1e1e", "log_fg": "#00ff00",
            "combobox_bg": "#4a4a4a", "combobox_fg": "#e0e0e0",
            "start_button_bg": "#28a745", "stop_button_bg": "#dc3545"
        }

        # Define specific dark mode themes with accents
        self.dark_purple_theme_colors = self.default_dark_theme_colors.copy()
        self.dark_purple_theme_colors.update({
            "start_button_bg": "#8A2BE2", # BlueViolet
            "stop_button_bg": "#8B008B",  # DarkMagenta
            "active_button_bg": "#9932CC", # DarkOrchid
            "log_fg": "#DA70D6" # Orchid
        })

        self.dark_red_theme_colors = self.default_dark_theme_colors.copy()
        self.dark_red_theme_colors.update({
            "start_button_bg": "#DC143C", # Crimson
            "stop_button_bg": "#8B0000",  # DarkRed
            "active_button_bg": "#A52A2A", # Brown
            "log_fg": "#FF6347" # Tomato
        })

        # Master dictionary of all preset themes
        self.preset_themes = {
            "Light Mode": self.default_light_theme_colors,
            "Dark Mode - Default": self.default_dark_theme_colors,
            "Dark Mode - Purple": self.dark_purple_theme_colors,
            "Dark Mode - Red": self.dark_red_theme_colors
        }
        self.user_defined_themes = {} # New: To store themes created by the user

        # Variable to hold the name of the currently selected theme
        self.current_theme_name = tk.StringVar(value="Light Mode") # Initial selection

        # Reference to the currently active theme config (can be a user-modified copy of a preset)
        self.active_theme_config = self.preset_themes["Light Mode"].copy() # Initialize with a copy of light theme

        # --- Variables for input fields ---
        self.cs2_exe_path = tk.StringVar(value="")
        self.pc_ip_address = tk.StringVar(value="")
        self.map_name = tk.StringVar(value="de_dust2")
        self.max_players = tk.StringVar(value="10")
        self.server_port = tk.StringVar(value="27015")
        self.server_password = tk.StringVar(value="")
        self.rcon_password = tk.StringVar(value="")

        # Combined Game Modes dropdown
        self.all_game_modes = {
            "Casual": ("0", "0"),
            "Competitive": ("0", "1"),
            "Wingman": ("0", "2"),
            "Arms Race": ("1", "0"),
            "Deathmatch": ("1", "2"),
        }

        self.selected_game_mode_display = tk.StringVar(value="Casual")
        self.additional_args = tk.StringVar(value="-usercon -dedicated")

        # --- Comprehensive CS2 Map List ---
        self.cs2_maps = {
            "Active Duty/Premier": [
                "de_ancient", "de_anubis", "de_dust2", "de_inferno",
                "de_mirage", "de_nuke", "de_overpass", "de_vertigo"
            ],
            "Reserve/Other Bomb Defusal": [
                "de_train", "de_basalt", "de_edin", "de_palais",
                "de_whistle"
            ],
            "Hostage Rescue": [
                "cs_office", "cs_italy", "cs_agency"
            ],
            "Arms Race": [
                "ar_baggage", "ar_shoots", "ar_pool_day"
            ],
            "Wingman (adapted for 2v2)": [
                "de_shortdust", "de_lake", "de_vertigo", "de_overpass",
                "de_nuke", "de_inferno", "de_ancient", "de_mirage",
                "de_memento", "de_assembly"
            ]
        }

        self.flattened_map_list = sorted(list(set(
            map_name for category in self.cs2_maps.values() for map_name in category
        )))

        self.credits_content = (
            "CS2 Dedicated Server Launcher\n"
            "Version 1.2.1\n\n"
            "Developed by Tarek\n"
            "Special thanks to CS2's Inability to directly host Dedicated Servers.\n\n"
        )

        self.create_widgets()
        self.auto_detect_cs2_path()
        # Apply the initial preset theme
        self.apply_preset_theme() # Will use self.current_theme_name.get()

    def add_tooltip(self, widget, text):
        """Helper method to add a tooltip to a widget."""
        ToolTip(widget, text)

    def create_widgets(self):
        # Top Frame for Credits, Settings and Theme Dropdown
        top_frame = tk.Frame(self.master)
        top_frame.pack(fill="x", anchor="ne", padx=10, pady=5)
        self.top_frame = top_frame # Store for theming

        self.credits_button = tk.Button(top_frame, text="Credits", command=self.show_credits)
        self.credits_button.pack(side="right")
        self.add_tooltip(self.credits_button, "View application credits and version information.")
        
        self.settings_button = tk.Button(top_frame, text="Settings", command=self.open_settings_window)
        self.settings_button.pack(side="right", padx=5)
        self.add_tooltip(self.settings_button, "Open color customization settings.")

        # Theme selection dropdown (replacing the toggle button)
        self.theme_combobox = ttk.Combobox(
            top_frame,
            textvariable=self.current_theme_name,
            values=[], # Will be populated by _update_theme_combobox_values
            state="readonly",
            width=20
        )
        self.theme_combobox.pack(side="right", padx=5)
        self.theme_combobox.bind("<<ComboboxSelected>>", self.apply_preset_theme)
        self.add_tooltip(self.theme_combobox, "Select a predefined or custom theme for the application.")
        self._update_theme_combobox_values() # Initial population of combobox values after all themes are defined
        self.theme_combobox.set(self.current_theme_name.get()) # Set initial display value


        # Input Frame
        input_frame = tk.LabelFrame(self.master, text="Server Parameters", padx=10, pady=10)
        input_frame.pack(padx=10, pady=(0, 10), fill="x")
        self.input_frame = input_frame # Store for theming

        input_frame.grid_columnconfigure(0, weight=0)
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_columnconfigure(2, weight=0)
        input_frame.grid_columnconfigure(3, weight=0)

        # Storing labels and entries for theming
        self.label_exe_path = tk.Label(input_frame, text="CS2 Server Exe Path:")
        self.label_exe_path.grid(row=0, column=0, sticky="w", pady=2)
        self.exe_path_entry = tk.Entry(input_frame, textvariable=self.cs2_exe_path, width=50)
        self.exe_path_entry.grid(row=0, column=1, pady=2, padx=5, sticky="ew")
        self.add_tooltip(self.exe_path_entry, "The full path to your CS2 dedicated server executable (cs2.exe).")

        self.browse_button = tk.Button(input_frame, text="Browse", command=self.browse_exe_path)
        self.browse_button.grid(row=0, column=2, pady=2)
        self.add_tooltip(self.browse_button, "Browse your file system to locate 'cs2.exe'.")

        self.auto_detect_button = tk.Button(input_frame, text="Auto-Detect CS2 Exe", command=self.auto_detect_cs2_path)
        self.auto_detect_button.grid(row=0, column=3, pady=2, padx=5)
        self.add_tooltip(self.auto_detect_button, "Automatically attempt to find the CS2 dedicated server executable.")

        self.label_ip = tk.Label(input_frame, text="PC IP Address:")
        self.label_ip.grid(row=1, column=0, sticky="w", pady=2)
        self.ip_entry = tk.Entry(input_frame, textvariable=self.pc_ip_address, width=50)
        self.ip_entry.grid(row=1, column=1, pady=2, padx=5, sticky="ew")
        self.add_tooltip(self.ip_entry, "Your PC's local IP address that the server will bind to. Leave blank to auto-detect.")

        self.detect_ip_button = tk.Button(input_frame, text="Detect IP", command=self.detect_ip_address)
        self.detect_ip_button.grid(row=1, column=2, pady=2)
        self.add_tooltip(self.detect_ip_button, "Attempt to automatically detect your local IP address.")

        self.label_map = tk.Label(input_frame, text="Map Name:")
        self.label_map.grid(row=2, column=0, sticky="w", pady=2)
        self.map_combobox = ttk.Combobox(
            input_frame,
            textvariable=self.map_name,
            values=self.flattened_map_list,
            state="readonly",
            width=48
        )
        self.map_combobox.grid(row=2, column=1, pady=2, padx=5, sticky="ew")
        self.map_combobox.set("de_dust2")
        self.add_tooltip(self.map_combobox, "Select the initial map for the server to load. Ensure it matches your chosen game mode.")

        self.label_max_players = tk.Label(input_frame, text="Max Players:")
        self.label_max_players.grid(row=3, column=0, sticky="w", pady=2)
        self.max_players_entry = tk.Entry(input_frame, textvariable=self.max_players, width=50)
        self.max_players_entry.grid(row=3, column=1, pady=2, padx=5, sticky="ew")
        self.add_tooltip(self.max_players_entry, "The maximum number of players allowed on the server (1-64).")

        self.label_server_port = tk.Label(input_frame, text="Server Port:")
        self.label_server_port.grid(row=4, column=0, sticky="w", pady=2)
        self.server_port_entry = tk.Entry(input_frame, textvariable=self.server_port, width=50)
        self.server_port_entry.grid(row=4, column=1, pady=2, padx=5, sticky="ew")
        self.add_tooltip(self.server_port_entry, "The UDP port the server will listen on (default is 27015). Ensure it's forwarded in your router if hosting externally.")

        self.label_server_password = tk.Label(input_frame, text="Server Password (Optional):")
        self.label_server_password.grid(row=5, column=0, sticky="w", pady=2)
        self.server_password_entry = tk.Entry(input_frame, textvariable=self.server_password, width=50, show="*")
        self.server_password_entry.grid(row=5, column=1, pady=2, padx=5, sticky="ew")
        self.add_tooltip(self.server_password_entry, "Set a password for your server. Players will need this to join.")

        self.label_rcon_password = tk.Label(input_frame, text="RCON Password (Optional):")
        self.label_rcon_password.grid(row=6, column=0, sticky="w", pady=2)
        self.rcon_password_entry = tk.Entry(input_frame, textvariable=self.rcon_password, width=50, show="*")
        self.rcon_password_entry.grid(row=6, column=1, pady=2, padx=5, sticky="ew")
        self.add_tooltip(self.rcon_password_entry, "Set an RCON password for remote server administration.")

        self.label_game_mode = tk.Label(input_frame, text="Game Mode:")
        self.label_game_mode.grid(row=7, column=0, sticky="w", pady=2)
        self.game_mode_combobox = ttk.Combobox(
            input_frame,
            textvariable=self.selected_game_mode_display,
            values=list(self.all_game_modes.keys()),
            state="readonly",
            width=48
        )
        self.game_mode_combobox.grid(row=7, column=1, pady=2, padx=5, sticky="ew")
        self.game_mode_combobox.set("Casual")
        self.add_tooltip(self.game_mode_combobox, "Select the game mode for your server (e.g., Casual, Competitive, Arms Race).")

        self.label_additional_args = tk.Label(input_frame, text="Additional Args:")
        self.label_additional_args.grid(row=8, column=0, sticky="w", pady=2)
        self.additional_args_entry = tk.Entry(input_frame, textvariable=self.additional_args, width=50)
        self.additional_args_entry.grid(row=8, column=1, pady=2, padx=5, sticky="ew")
        self.add_tooltip(self.additional_args_entry, "Add any extra command-line arguments for the server (e.g., -tickrate 128, +sv_cheats 1).")

        # Command Buttons
        button_frame = tk.Frame(self.master, padx=10, pady=5)
        button_frame.pack(pady=5)
        self.button_frame = button_frame # Store for theming

        self.start_button = tk.Button(button_frame, text="Start Server", command=self.start_server, width=15, height=2)
        self.start_button.pack(side="left", padx=10)
        self.add_tooltip(self.start_button, "Start the CS2 dedicated server with the specified parameters.")

        self.stop_button = tk.Button(button_frame, text="Stop Server", command=self.stop_server, width=15, height=2)
        self.stop_button.pack(side="left", padx=10)
        self.add_tooltip(self.stop_button, "Stop the currently running CS2 dedicated server.")

        self.save_config_button = tk.Button(button_frame, text="Save Config", command=self.save_config, width=15, height=2)
        self.save_config_button.pack(side="left", padx=10)
        self.add_tooltip(self.save_config_button, "Save current server settings to a configuration file.")

        self.load_config_button = tk.Button(button_frame, text="Load Config", command=self.load_config, width=15, height=2)
        self.load_config_button.pack(side="left", padx=10)
        self.add_tooltip(self.load_config_button, "Load server settings from a configuration file.")

        # Console Command Input
        command_frame = tk.Frame(self.master, padx=10, pady=5)
        command_frame.pack(padx=10, pady=(0, 10), fill="x")
        self.command_frame = command_frame # Store for theming
        
        self.command_label = tk.Label(command_frame, text="Console Command:")
        self.command_label.pack(side="left", padx=(0, 5))
        self.add_tooltip(self.command_label, "Enter a console command to send to the server (e.g., 'sv_cheats 1', 'changelevel de_mirage').")

        self.command_entry = tk.Entry(command_frame, textvariable=tk.StringVar(), width=60)
        self.command_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.command_entry.bind("<Return>", self.send_command_on_enter) # Bind Enter key
        self.add_tooltip(self.command_entry, "Type your console command here and press Enter or click 'Send Command'.")

        self.send_command_button = tk.Button(command_frame, text="Send Command", command=self.send_console_command)
        self.send_command_button.pack(side="left")
        self.add_tooltip(self.send_command_button, "Send the entered command to the server.")


        # Log Frame
        log_frame = tk.LabelFrame(self.master, text="Server Output Log", padx=10, pady=10)
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.log_frame = log_frame # Store for theming

        self.log_text = tk.Text(log_frame, height=10, state="disabled", wrap="word", font=("Consolas", 10))
        self.log_text.pack(side="left", fill="both", expand=True)
        self.log_text_scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text_scroll.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=self.log_text_scroll.set)
        self.add_tooltip(self.log_text, "Displays real-time output and logs from the CS2 dedicated server.")

    def _update_theme_combobox_values(self):
        """Updates the values in the theme combobox to include all preset and user-defined themes."""
        combined_theme_names = sorted(list(self.preset_themes.keys()) + list(self.user_defined_themes.keys()))
        self.theme_combobox["values"] = combined_theme_names
        # Ensure the selected theme is still in the list, or default
        if self.current_theme_name.get() not in combined_theme_names:
            if "Light Mode" in combined_theme_names:
                self.current_theme_name.set("Light Mode")
                self.theme_combobox.set("Light Mode")
            elif combined_theme_names: # Fallback to first available if Light Mode not there
                self.current_theme_name.set(combined_theme_names[0])
                self.theme_combobox.set(combined_theme_names[0])
            else: # No themes at all (shouldn't happen with default presets)
                self.current_theme_name.set("")
                self.theme_combobox.set("")

    def apply_theme(self, theme_config_dict):
        """Applies the specified theme (color dictionary) to all widgets."""
        self.active_theme_config = theme_config_dict.copy() # Store a mutable copy for settings
        theme = self.active_theme_config
        
        # Update master window
        self.master.config(bg=theme["bg"])
        self.master.update_idletasks() # Force update after changing master background

        # Update frames and labels
        for frame in [self.top_frame, self.input_frame, self.button_frame, self.log_frame, self.command_frame]:
            frame.config(bg=theme["frame_bg"])
            self.master.update_idletasks() # Update after each frame, if many frames

        for label in [
            self.label_exe_path, self.label_ip, self.label_map, self.label_max_players,
            self.label_server_port, self.label_server_password, self.label_rcon_password,
            self.label_game_mode, self.label_additional_args, self.command_label
        ]:
            label.config(bg=theme["frame_bg"], fg=theme["frame_fg"])

        # Update Entry widgets
        for entry in [
            self.exe_path_entry, self.ip_entry, self.max_players_entry,
            self.server_port_entry, self.server_password_entry, self.rcon_password_entry,
            self.additional_args_entry, self.command_entry
        ]:
            entry.config(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"])

        # Update Comboboxes (ttk styles)
        style = ttk.Style()
        style.theme_use('clam') 

        # Configure the general TCombobox style
        style.configure("TCombobox",
                        fieldbackground=theme["combobox_bg"],
                        background=theme["button_bg"], # Background of the dropdown arrow area
                        foreground=theme["combobox_fg"],
                        selectbackground=theme["button_bg"], # Background when text is selected within the combobox
                        selectforeground=theme["combobox_fg"],
                        arrowcolor=theme["button_fg"], # Color of the dropdown arrow
                        bordercolor=theme["button_bg"], # Border around the combobox
                        lightcolor=theme["button_bg"],
                        darkcolor=theme["button_bg"])

        # Map to handle state changes (e.g., when combobox is readonly)
        style.map('TCombobox',
                  fieldbackground=[('readonly', theme["combobox_bg"])],
                  background=[('readonly', theme["button_bg"])],
                  foreground=[('readonly', theme["combobox_fg"])],
                  selectbackground=[('readonly', theme["button_bg"])],
                  selectforeground=[('readonly', theme["combobox_fg"])])
        
        self.master.update_idletasks() # Update after ttk style changes

        # Update regular Buttons
        for button in [
            self.credits_button, self.browse_button,
            self.auto_detect_button, self.detect_ip_button, self.settings_button,
            self.save_config_button, self.load_config_button, self.send_command_button
        ]:
            button.config(bg=theme["button_bg"], fg=theme["button_fg"],
                          activebackground=theme["active_button_bg"], activeforeground=theme["active_button_fg"])
        
        # Special buttons (Start/Stop)
        self.start_button.config(bg=theme["start_button_bg"], fg="white",
                                 activebackground=theme["start_button_bg"], activeforeground="white")
        self.stop_button.config(bg=theme["stop_button_bg"], fg="white",
                                activebackground=theme["stop_button_bg"], activeforeground="white")
        self.master.update_idletasks() # Update after special buttons

        # Update Text widget (log_text)
        self.log_text.config(bg=theme["log_bg"], fg=theme["log_fg"])
        self.log_text_scroll.config(bg=theme["button_bg"]) # Scrollbar background
        self.master.update_idletasks() # Final update

    def apply_preset_theme(self, event=None):
        """Applies the theme selected from the preset dropdown (either default or user-defined)."""
        selected_theme_name = self.current_theme_name.get()
        
        theme_config_dict = self.preset_themes.get(selected_theme_name)
        if not theme_config_dict: # Not found in default presets, check user-defined
            theme_config_dict = self.user_defined_themes.get(selected_theme_name)

        if theme_config_dict:
            # We want to apply a COPY of the preset/user-defined theme,
            # so modifications in settings don't change the original preset/user-defined definition.
            self.apply_theme(theme_config_dict.copy()) # Pass a copy
        else:
            self.append_to_log(f"Warning: Theme '{selected_theme_name}' not found in any theme collection. Falling back to Light Mode.")
            # Fallback to default light theme if selected theme is not found
            self.current_theme_name.set("Light Mode")
            self.theme_combobox.set("Light Mode")
            self.apply_theme(self.preset_themes["Light Mode"].copy())

    def show_credits(self):
        """Displays the credits information in a message box."""
        messagebox.showinfo("Credits", self.credits_content)

    def open_settings_window(self):
        """Opens a new window for color customization settings."""
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Color Settings")
        settings_window.geometry("450x550")
        settings_window.resizable(False, False)
        settings_window.transient(self.master) # Make it appear on top of the main window
        settings_window.grab_set() # Make it modal

        settings_window.config(bg=self.active_theme_config["bg"]) # Use active_theme_config

        # Mapping of theme keys to display names for settings
        color_map = {
            "bg": "General Background",
            "fg": "General Text Color",
            "frame_bg": "Frame Background",
            "frame_fg": "Frame Title Color", # Affects LabelFrame title
            "entry_bg": "Entry Field Background",
            "entry_fg": "Entry Field Text",
            "button_bg": "Normal Button Background",
            "button_fg": "Normal Button Text",
            "log_bg": "Log Area Background",
            "log_fg": "Log Area Text",
            "start_button_bg": "Start Button Background",
            "stop_button_bg": "Stop Button Background"
        }

        row = 0
        current_theme_for_settings = self.active_theme_config # Directly modify the active theme

        # Store references to color display frames for dynamic updates
        color_display_frames = {}

        def create_color_picker_row(parent_frame, label_text, color_key, current_color):
            nonlocal row
            tk.Label(parent_frame, text=label_text, bg=current_theme_for_settings["frame_bg"], fg=current_theme_for_settings["frame_fg"]).grid(row=row, column=0, sticky="w", pady=2, padx=5)
            
            # Display current color
            color_frame = tk.Frame(parent_frame, width=20, height=20, bg=current_color, relief="solid", borderwidth=1)
            color_frame.grid(row=row, column=1, pady=2, padx=5, sticky="w")
            color_display_frames[color_key] = color_frame # Store reference

            def pick_color():
                chosen_color = colorchooser.askcolor(title=f"Choose {label_text} Color", initialcolor=current_theme_for_settings[color_key])
                if chosen_color and chosen_color[1]: # chosen_color is (RGB_tuple, hex_string)
                    new_color_hex = chosen_color[1]
                    current_theme_for_settings[color_key] = new_color_hex
                    # When a color is changed in settings, update the active_theme_config and re-apply
                    self.apply_theme(self.active_theme_config) # Re-apply the modified active theme
                    color_frame.config(bg=new_color_hex) # Update settings window display

            button = tk.Button(parent_frame, text="Change Color", command=pick_color,
                               bg=current_theme_for_settings["button_bg"], fg=current_theme_for_settings["button_fg"],
                               activebackground=current_theme_for_settings["active_button_bg"], activeforeground=current_theme_for_settings["active_button_fg"])
            button.grid(row=row, column=2, pady=2, padx=5)
            row += 1

        # Use the name of the currently active theme in the settings window title
        settings_frame = tk.LabelFrame(settings_window, text=f"Customize '{self.current_theme_name.get()}' Theme Colors", 
                                       padx=10, pady=10, bg=current_theme_for_settings["frame_bg"], fg=current_theme_for_settings["frame_fg"])
        settings_frame.pack(padx=10, pady=10, fill="both", expand=True)

        for key, display_name in color_map.items():
            create_color_picker_row(settings_frame, display_name, key, current_theme_for_settings.get(key, "#000000")) # Provide a fallback color

        def reset_colors():
            # Get the original preset colors (either from default or user-defined)
            original_preset_colors = None
            selected_theme_name_for_reset = self.current_theme_name.get()
            if selected_theme_name_for_reset in self.preset_themes:
                original_preset_colors = self.preset_themes[selected_theme_name_for_reset].copy()
            elif selected_theme_name_for_reset in self.user_defined_themes:
                original_preset_colors = self.user_defined_themes[selected_theme_name_for_reset].copy()
            else:
                messagebox.showwarning("Error", "Could not find original theme colors to reset for the current theme.")
                return

            self.active_theme_config.update(original_preset_colors) # Update the active config with original preset colors
            self.apply_theme(self.active_theme_config) # Re-apply the reset active theme

            # Update settings window display as well
            updated_theme = self.active_theme_config # Now this holds the reset colors
            settings_frame.config(bg=updated_theme["frame_bg"], fg=updated_theme["frame_fg"])
            for child in settings_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(bg=updated_theme["frame_bg"], fg=updated_theme["frame_fg"])
                elif isinstance(child, tk.Button):
                    if child["text"] == "Reset All Colors to Default":
                        child.config(bg=updated_theme["button_bg"], fg=updated_theme["button_fg"],
                                     activebackground=updated_theme["active_button_bg"], activeforeground=updated_theme["button_fg"])
                    else: # For the "Change Color" buttons
                        child.config(bg=updated_theme["button_bg"], fg=updated_theme["button_fg"],
                                     activebackground=updated_theme["active_button_bg"], activeforeground=updated_theme["button_fg"])
            for key, frame in color_display_frames.items(): # Update color display frames
                frame.config(bg=updated_theme.get(key, "#000000")) 

            messagebox.showinfo("Colors Reset", f"Colors for '{self.current_theme_name.get()}' theme have been reset to default values.")

        reset_button = tk.Button(settings_window, text="Reset All Colors to Default", command=reset_colors,
                                bg=current_theme_for_settings["button_bg"], fg=current_theme_for_settings["button_fg"],
                                activebackground=current_theme_for_settings["active_button_bg"], activeforeground=current_theme_for_settings["button_fg"])
        reset_button.pack(pady=10)

        # Add "Save Current Theme As" button
        save_theme_button = tk.Button(settings_window, text="Save Current Theme As...", command=self.save_current_theme_as_preset,
                                bg=current_theme_for_settings["button_bg"], fg=current_theme_for_settings["button_fg"],
                                activebackground=current_theme_for_settings["active_button_bg"], activeforeground=current_theme_for_settings["button_fg"])
        save_theme_button.pack(pady=5) # Below Reset button

        # Handle closing of the settings window
        settings_window.protocol("WM_DELETE_WINDOW", settings_window.destroy)

    def save_current_theme_as_preset(self):
        """Prompts user for a name and saves the current active theme as a new preset."""
        name_window = tk.Toplevel(self.master)
        name_window.title("Save Theme As")
        name_window.geometry("300x120")
        name_window.transient(self.master)
        name_window.grab_set()

        name_window.config(bg=self.active_theme_config["bg"])

        label = tk.Label(name_window, text="Enter a name for your theme:", 
                         bg=self.active_theme_config["frame_bg"], fg=self.active_theme_config["frame_fg"])
        label.pack(pady=10)

        theme_name_var = tk.StringVar()
        name_entry = tk.Entry(name_window, textvariable=theme_name_var, width=30,
                              bg=self.active_theme_config["entry_bg"], fg=self.active_theme_config["entry_fg"], insertbackground=self.active_theme_config["entry_fg"])
        name_entry.pack(pady=5)
        name_entry.focus_set()

        def confirm_save():
            new_theme_name = theme_name_var.get().strip()
            if not new_theme_name:
                messagebox.showwarning("Input Error", "Theme name cannot be empty.")
                return
            
            # Combine preset and user-defined themes for validation
            all_theme_names = list(self.preset_themes.keys()) + list(self.user_defined_themes.keys())
            if new_theme_name in all_theme_names:
                messagebox.showwarning("Name Exists", f"A theme named '{new_theme_name}' already exists. Please choose a different name.")
                return

            # Save a copy of the current active theme config
            self.user_defined_themes[new_theme_name] = self.active_theme_config.copy()
            
            # Update combobox values
            self._update_theme_combobox_values()
            
            # Set the new theme as current and apply it
            self.current_theme_name.set(new_theme_name)
            self.theme_combobox.set(new_theme_name) # Update combobox display
            self.apply_theme(self.user_defined_themes[new_theme_name]) # Re-apply to ensure any new widget styling is picked up

            self.append_to_log(f"Theme '{new_theme_name}' saved successfully.")
            messagebox.showinfo("Theme Saved", f"Your theme '{new_theme_name}' has been saved.")
            name_window.destroy()

        save_button = tk.Button(name_window, text="Save", command=confirm_save,
                               bg=self.active_theme_config["button_bg"], fg=self.active_theme_config["button_fg"],
                               activebackground=self.active_theme_config["active_button_bg"], activeforeground=self.active_theme_config["active_button_fg"])
        save_button.pack(pady=10)

        name_window.protocol("WM_DELETE_WINDOW", name_window.destroy)

    def browse_exe_path(self):
        filepath = filedialog.askopenfilename(
            title="Select CS2 Dedicated Server Executable",
            filetypes=[("Executable files", "*.exe")]
        )
        if filepath:
            self.cs2_exe_path.set(filepath)
            self.append_to_log(f"CS2 executable path set to: {filepath}")

    def auto_detect_cs2_path(self):
        self.append_to_log("Attempting to auto-detect CS2 server executable...")
        steam_install_paths = self._find_steam_installations()
        found_path = None

        if not steam_install_paths:
            self.append_to_log("No common Steam installation paths found. Please ensure Steam is installed.")

        for steam_path in steam_install_paths:
            library_folders_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
            if os.path.exists(library_folders_path):
                self.append_to_log(f"Found libraryfolders.vdf at: {library_folders_path}")
                library_paths = self._parse_library_folders_vdf(library_folders_path)
                library_paths.insert(0, steam_path) # Add the main Steam path as a primary library

                for lib_path in library_paths:
                    cleaned_lib_path = lib_path.strip('"')
                    
                    cs2_appmanifest_path = os.path.join(cleaned_lib_path, "steamapps", "appmanifest_730.acf")
                    if os.path.exists(cs2_appmanifest_path):
                        self.append_to_log(f"Found appmanifest_730.acf at: {cs2_appmanifest_path}")
                        cs2_install_dir = self._parse_appmanifest_acf(cs2_appmanifest_path)
                        if cs2_install_dir:
                            potential_exe_path = os.path.join(
                                cleaned_lib_path,
                                "steamapps",
                                "common",
                                cs2_install_dir,
                                "game",
                                "bin",
                                "win64",
                                "cs2.exe"
                            )
                            if os.path.exists(potential_exe_path):
                                found_path = potential_exe_path
                                break # Found it, exit inner loop
                if found_path:
                    break # Found it, exit outer loop

        if found_path:
            self.cs2_exe_path.set(found_path)
            self.append_to_log(f"Auto-detected CS2 executable: {found_path}")
            messagebox.showinfo("Auto-Detection Complete", f"CS2 executable found at:\n{found_path}")
        else:
            self.append_to_log("Could not auto-detect CS2 executable. Please browse manually.")
            messagebox.showwarning("Auto-Detection Failed", "Could not automatically find CS2 executable.\nPlease browse for it manually.")

    def _find_steam_installations(self):
        paths = []
        # Common Steam installation paths
        program_files_x86 = os.environ.get("ProgramFiles(x86)")
        if program_files_x86:
            potential_path = os.path.join(program_files_x86, "Steam")
            if os.path.exists(potential_path):
                paths.append(potential_path)

        program_files = os.environ.get("ProgramFiles")
        if program_files and program_files_x86 != program_files: # Avoid duplicating if ProgramFiles(x86) is same as ProgramFiles
            potential_path = os.path.join(program_files, "Steam")
            if os.path.exists(potential_path):
                paths.append(potential_path)
        
        # Check specific drive letters and common Program Files locations
        drive_letters = ['C', 'D', 'E', 'F']
        install_folders = ["Steam", "Program Files\\Steam", "Program Files (x86)\\Steam"]

        for drive in drive_letters:
            for folder in install_folders:
                potential_path = os.path.join(f"{drive}:\\", folder)
                if os.path.exists(potential_path):
                    paths.append(potential_path)

        return list(set(paths)) # Return unique paths

    def _parse_library_folders_vdf(self, vdf_path):
        library_paths = []
        try:
            with open(vdf_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Regex to find "path" values within numerical sections (library folders)
            paths_found = re.findall(r'"\d+"\s*{\s*"path"\s*"(.*?)"', content, re.DOTALL)
            for p in paths_found:
                # Normalize paths: replace double backslashes with single, forward slashes with os.sep
                cleaned_path = p.replace("\\\\", "\\").replace("/", os.sep)
                if os.path.exists(cleaned_path):
                    library_paths.append(cleaned_path)
                else:
                    self.append_to_log(f"Warning: Found VDF library path that does not exist: {cleaned_path}")
        except Exception as e:
            self.append_to_log(f"Error parsing libraryfolders.vdf ({vdf_path}): {e}")
        return library_paths

    def _parse_appmanifest_acf(self, acf_path):
        install_dir = None
        try:
            with open(acf_path, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'"installdir"\s*"(.*?)"', content)
            if match:
                install_dir = match.group(1)
        except Exception as e:
            self.append_to_log(f"Error parsing appmanifest_730.acf ({acf_path}): {e}")
        return install_dir

    def detect_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Connect to a public IP to get the local IP used for outgoing connections
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            self.pc_ip_address.set(ip_address)
            self.append_to_log(f"Detected IP address: {ip_address}")
        except Exception as e:
            messagebox.showerror("IP Detection Error", f"Could not detect IP address: {e}\nPlease enter it manually.")
            self.append_to_log(f"Error detecting IP address: {e}")

    def append_to_log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def read_server_output(self):
        if self.server_process:
            while not self.stop_log_thread.is_set():
                # Readline with timeout for cleaner shutdown
                try:
                    line = self.server_process.stdout.readline()
                except ValueError: # stdin/stdout closed
                    break
                
                if not line:
                    if self.server_process.poll() is not None: # Process has terminated
                        break
                    time.sleep(0.1) # Short delay to prevent busy-waiting
                    continue
                try:
                    decoded_line = line.decode('utf-8', errors='replace').strip()
                    self.master.after(0, self.append_to_log, decoded_line)
                except Exception as e:
                    self.master.after(0, self.append_to_log, f"Error decoding line from server output: {e}")
            self.master.after(0, self.append_to_log, "Server output stream closed.")
        else:
            self.master.after(0, self.append_to_log, "No server process to read from.")


    def start_server(self):
        if self.server_process and self.server_process.poll() is None:
            messagebox.showinfo("Server Status", "Server is already running.")
            return

        exe_path = self.cs2_exe_path.get().strip()
        pc_ip = self.pc_ip_address.get().strip()
        selected_game_mode_name = self.selected_game_mode_display.get()
        map_name = self.map_name.get().strip()
        max_players = self.max_players.get().strip()
        server_port = self.server_port.get().strip()

        # --- Input Validation ---
        if not exe_path:
            messagebox.showerror("Error", "Please specify the path to the CS2 server executable.")
            return
        if not os.path.exists(exe_path):
            messagebox.showerror("Error", f"Executable not found at: {exe_path}")
            self.append_to_log(f"Error: Executable not found at {exe_path}")
            return
        if not pc_ip:
            messagebox.showerror("Error", "Please enter or detect your PC's IP address.")
            return
        if not map_name:
            messagebox.showerror("Error", "Please select a map name.")
            return
        if map_name not in self.flattened_map_list:
            messagebox.showwarning("Warning", "The selected map might not be an official CS2 map or may require workshop content. Proceed with caution.")
            self.append_to_log(f"Warning: Map '{map_name}' is not in the known official list. This might require workshop subscriptions or custom content setup.")

        try:
            max_players_int = int(max_players)
            if not (1 <= max_players_int <= 64):
                messagebox.showerror("Error", "Max Players must be a number between 1 and 64.")
                return
        except ValueError:
            messagebox.showerror("Error", "Max Players must be a valid number.")
            return
        try:
            server_port_int = int(server_port)
            if not (1024 <= server_port_int <= 65535):
                messagebox.showerror("Error", "Server Port must be a number between 1024 and 65535.")
                return
        except ValueError:
            messagebox.showerror("Error", "Server Port must be a valid number.")
            return

        # --- Game Mode and Map Logic (Enhanced) ---
        game_type_val, game_mode_val = self.all_game_modes.get(selected_game_mode_name, ("0", "0"))

        # Check for map type consistency with game mode
        map_prefix = map_name.split('_')[0].lower()
        
        if selected_game_mode_name == "Arms Race":
            if map_prefix != "ar":
                messagebox.showwarning(
                    "Map Warning",
                    f"Arms Race is typically played on 'ar_' maps (e.g., 'ar_baggage'). "
                    f"You have selected '{map_name}'. The server might not function as expected."
                )
                self.append_to_log(
                    f"Warning: Arms Race selected with map '{map_name}'. "
                    "Typically played on specific Arms Race maps (e.g., 'ar_baggage')."
                )
        elif selected_game_mode_name == "Wingman":
            # Wingman typically uses adapted 'de_' maps or specific wingman maps
            wingman_map_prefixes = ["de", "wm"] # wm_ prefix if any official wingman maps
            if map_prefix not in wingman_map_prefixes:
                messagebox.showwarning(
                    "Map Warning",
                    f"Wingman is typically played on adapted 'de_' maps (e.g., 'de_shortdust', 'de_lake'). "
                    f"You have selected '{map_name}'. The server might not function as expected."
                )
                self.append_to_log(
                    f"Warning: Wingman selected with map '{map_name}'. "
                    "Typically played on specific adapted maps."
                )
        elif selected_game_mode_name in ["Casual", "Competitive"]:
            if map_prefix not in ["de", "cs"]: # Bomb Defusal or Hostage Rescue
                messagebox.showwarning(
                    "Map Warning",
                    f"{selected_game_mode_name} mode is typically played on 'de_' or 'cs_' maps. "
                    f"You have selected '{map_name}'. This might lead to unexpected server behavior."
                )
                self.append_to_log(
                    f"Warning: {selected_game_mode_name} mode selected with a non-'de_'/non-'cs_' map ('{map_name}')."
                )
        elif selected_game_mode_name == "Deathmatch":
            # Deathmatch can be played on any map, but typically uses de_ or cs_ maps
            pass # No specific prefix check, as it's flexible

        # --- Construct Command Arguments ---
        cmd_args = [
            f"-dedicated",
            f"-ip {pc_ip}",
            f"-port {server_port}",
            f"+game_type {game_type_val}",
            f"+game_mode {game_mode_val}",
            f"+map {map_name}",
            f"-maxplayers {max_players}",
        ]

        if self.server_password.get():
            cmd_args.append(f"+sv_password \"{self.server_password.get()}\"")
        if self.rcon_password.get():
            cmd_args.append(f"+rcon_password \"{self.rcon_password.get()}\"")

        if self.additional_args.get():
            try:
                # shlex.split handles quoted arguments correctly
                additional_parsed_args = shlex.split(self.additional_args.get())
                cmd_args.extend(additional_parsed_args)
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid Additional Arguments format: {e}")
                self.append_to_log(f"Error parsing additional arguments: {e}")
                return

        full_command = [exe_path] + cmd_args

        try:
            # Determine the working directory for the server process
            # It should be the directory containing 'game' folder, usually Steam/steamapps/common/Counter-Strike Global Offensive
            server_bin_path = os.path.dirname(exe_path) # e.g., .../win64
            server_game_path = os.path.dirname(server_bin_path) # e.g., .../bin
            server_base_path = os.path.dirname(server_game_path) # e.g., .../game
            server_dir = os.path.dirname(server_base_path) # e.g., .../Counter-Strike Global Offensive

            creation_flags = 0
            if os.name == 'nt': # For Windows, hide the console window
                creation_flags = subprocess.CREATE_NO_WINDOW

            self.server_process = subprocess.Popen(
                full_command,
                cwd=server_dir, # Set working directory to the CS2 install root
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Redirect stderr to stdout for combined log
                text=False, # Output is bytes, needs decoding
                creationflags=creation_flags
                # If you want to enable sending commands via stdin, add:
                # stdin=subprocess.PIPE
            )
            self.append_to_log(f"Starting server with command: {' '.join(shlex.quote(arg) for arg in full_command)}")
            self.append_to_log(f"Working directory set to: {server_dir}")
            self.append_to_log("Server process started. Please wait for it to load.")

            self.stop_log_thread.clear() # Ensure the event is clear for a new thread
            self.output_log_thread = threading.Thread(target=self.read_server_output)
            self.output_log_thread.daemon = True # Daemonize thread so it exits with main app
            self.output_log_thread.start()

        except FileNotFoundError:
            messagebox.showerror("Error", f"The executable '{exe_path}' was not found. Please check the path.")
            self.append_to_log(f"Error: Executable not found at {exe_path}")
            self.server_process = None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")
            self.append_to_log(f"Error starting server: {e}")
            self.server_process = None

    def stop_server(self):
        if self.server_process and self.server_process.poll() is None:
            self.append_to_log("Attempting to stop server...")
            try:
                self.stop_log_thread.set() # Signal the log thread to stop
                if self.output_log_thread and self.output_log_thread.is_alive():
                    self.output_log_thread.join(timeout=3) # Wait for log thread to finish

                self.server_process.terminate() # Request graceful termination
                self.append_to_log("Sent terminate signal to server process.")

                try:
                    self.server_process.wait(timeout=10) # Wait a bit for it to close
                    if self.server_process.poll() is None: # Still running?
                        self.server_process.kill() # Force kill
                        self.append_to_log("Server process forcefully terminated.")
                    else:
                        self.append_to_log("Server process terminated successfully.")
                except subprocess.TimeoutExpired:
                    self.server_process.kill() # Force kill if timeout
                    self.append_to_log("Server process did not terminate in time, forcefully killed.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop server: {e}")
                self.append_to_log(f"Error stopping server: {e}")
            finally:
                self.server_process = None
                self.output_log_thread = None
                self.stop_log_thread.clear() # Clear for next start
        else:
            messagebox.showinfo("Server Status", "No server process is currently running.")
            # Ensure state is clean even if process somehow detached but wasn't None
            if self.server_process:
                self.server_process = None
                self.output_log_thread = None
                self.stop_log_thread.clear()

    def send_console_command(self):
        """Sends a console command to the running server."""
        if not self.server_process or self.server_process.poll() is not None:
            messagebox.showwarning("Server Not Running", "No server is currently running to send commands to.")
            self.append_to_log("Cannot send command: Server not running.")
            return

        command = self.command_entry.get().strip()
        if not command:
            messagebox.showwarning("Empty Command", "Please enter a command to send.")
            return

        try:
            self.append_to_log(f"Attempting to send command: {command}")
            messagebox.showinfo("Command Sent (Logged)", 
                                f"Command '{command}' sent. Note: Direct console command sending via GUI might not be fully supported by CS2 dedicated server stdout/stdin. "
                                "For robust command execution, consider implementing RCON.")

            # Clear the command entry after sending
            self.command_entry.delete(0, tk.END)

        except Exception as e:
            self.append_to_log(f"Error sending command: {e}")
            messagebox.showerror("Command Error", f"Failed to send command: {e}")

    def send_command_on_enter(self, event=None):
        """Called when the Enter key is pressed in the command entry."""
        self.send_console_command()

    def save_config(self):
        """Saves current server configuration and custom theme colors to a JSON file."""
        config_data = {
            "cs2_exe_path": self.cs2_exe_path.get(),
            "pc_ip_address": self.pc_ip_address.get(),
            "map_name": self.map_name.get(),
            "max_players": self.max_players.get(),
            "server_port": self.server_port.get(),
            "server_password": self.server_password.get(),
            "rcon_password": self.rcon_password.get(),
            "selected_game_mode_display": self.selected_game_mode_display.get(),
            "additional_args": self.additional_args.get(),
            "current_theme_name": self.current_theme_name.get(), # Save the selected preset name
            "active_theme_config_colors": self.active_theme_config, # Save the currently active (potentially customized) colors
            "user_defined_themes": self.user_defined_themes # Save user-defined themes
        }

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Server Configuration"
        )
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    json.dump(config_data, f, indent=4)
                self.append_to_log(f"Configuration saved to: {filepath}")
                messagebox.showinfo("Save Config", "Configuration saved successfully!")
            except Exception as e:
                self.append_to_log(f"Error saving configuration: {e}")
                messagebox.showerror("Save Config Error", f"Failed to save configuration: {e}")

    def load_config(self):
        """Loads server configuration and custom theme colors from a JSON file."""
        filepath = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Server Configuration"
        )
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    config_data = json.load(f)
                
                # Update Tkinter variables
                self.cs2_exe_path.set(config_data.get("cs2_exe_path", ""))
                self.pc_ip_address.set(config_data.get("pc_ip_address", ""))
                self.map_name.set(config_data.get("map_name", "de_dust2"))
                self.max_players.set(config_data.get("max_players", "10"))
                self.server_port.set(config_data.get("server_port", "27015"))
                self.server_password.set(config_data.get("server_password", ""))
                self.rcon_password.set(config_data.get("rcon_password", ""))
                self.selected_game_mode_display.set(config_data.get("selected_game_mode_display", "Casual"))
                self.additional_args.set(config_data.get("additional_args", "-usercon -dedicated"))
                
                # Load theme preference and colors
                loaded_theme_name = config_data.get("current_theme_name", "Light Mode")
                loaded_active_colors = config_data.get("active_theme_config_colors", None)
                loaded_user_defined_themes = config_data.get("user_defined_themes", {}) # Load user-defined themes

                self.user_defined_themes = loaded_user_defined_themes # Update user-defined themes dictionary
                self._update_theme_combobox_values() # Refresh combobox with newly loaded user themes

                self.current_theme_name.set(loaded_theme_name)
                self.theme_combobox.set(loaded_theme_name) 

                if loaded_active_colors:
                    # If specific customized colors were saved, use them directly
                    self.apply_theme(loaded_active_colors)
                else:
                    # Otherwise, apply the preset based on the loaded name (for older configs or if no custom colors were saved)
                    self.apply_preset_theme() 

                self.append_to_log(f"Configuration loaded from: {filepath}")
                messagebox.showinfo("Load Config", "Configuration loaded successfully!")
            except FileNotFoundError:
                self.append_to_log(f"Error: Configuration file not found at {filepath}")
                messagebox.showerror("Load Config Error", "Configuration file not found.")
            except json.JSONDecodeError as e:
                self.append_to_log(f"Error decoding JSON from configuration file: {e}")
                messagebox.showerror("Load Config Error", f"Invalid configuration file format: {e}")
            except Exception as e:
                self.append_to_log(f"Error loading configuration: {e}")
                messagebox.showerror("Load Config Error", f"Failed to load configuration: {e}")

    def on_closing(self):
        if self.server_process and self.server_process.poll() is None:
            if messagebox.askokcancel("Quit", "A server is currently running. Do you want to quit and stop the server?"):
                self.stop_server()
                self.master.destroy()
        else:
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CS2ServerLauncher(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()