import tkinter as tk
from tkinter import messagebox, filedialog, ttk, colorchooser
import subprocess
import os
import threading
import time
import shlex
import json

# Import classes and functions from new files
from tooltip import ToolTip
from server_utils import auto_detect_cs2_path, detect_ip_address, _parse_appmanifest_acf, _parse_library_folders_vdf, _find_steam_installations


class CS2ServerLauncher:
    def __init__(self, master):
        self.master = master
        master.title("CS2 Dedicated Server Launcher")
        master.geometry("1100x750") # Wider for horizontal layout
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
            "log_bg": "white", "log_fg": "black",
            "pb_trough_bg": "#e1e1e1", "pb_chunk_bg": "#4CAF50",
            "tooltip_bg": "#FFFFCC", "tooltip_fg": "black",
            "dropdown_bg": "white", "dropdown_fg": "black", "dropdown_active_bg": "#c8c8c8", "dropdown_active_fg": "black",
        }

        self.default_dark_theme_colors = {
            "bg": "#2b2b2b", "fg": "#cccccc",
            "frame_bg": "#2b2b2b", "frame_fg": "#cccccc",
            "entry_bg": "#3c3c3c", "entry_fg": "#cccccc",
            "button_bg": "#3c3c3c", "button_fg": "#cccccc",
            "active_button_bg": "#505050", "active_button_fg": "#ffffff",
            "log_bg": "#1e1e1e", "log_fg": "#cccccc",
            "pb_trough_bg": "#3c3c3c", "pb_chunk_bg": "#5cb85c",
            "tooltip_bg": "#444444", "tooltip_fg": "#ffffff",
            "dropdown_bg": "#3c3c3c", "dropdown_fg": "#cccccc", "dropdown_active_bg": "#505050", "dropdown_active_fg": "#ffffff",
        }

        self.current_theme_colors = {}
        self.is_dark_mode = False
        self.custom_colors = {
            "light": {},
            "dark": {}
        }
        self.current_preset_name = "Default Light" # To store the name of the active preset

        self.create_widgets()
        self.apply_theme(self.is_dark_mode) # Apply initial theme
        self.auto_detect_cs2_path()


    def create_widgets(self):
        # Frame for server path configuration
        path_frame = ttk.LabelFrame(self.master, text="CS2 Server Path")
        path_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
        self.master.grid_columnconfigure(0, weight=1)

        self.path_entry = ttk.Entry(path_frame, width=80)
        self.path_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.path_entry.insert(0, os.path.join(os.getcwd(), "cs2_server")) # Default path
        ToolTip(self.path_entry, "Path to your CS2 dedicated server installation.")

        browse_button = ttk.Button(path_frame, text="Browse", command=self.browse_path)
        browse_button.grid(row=0, column=1, padx=5, pady=5)
        ToolTip(browse_button, "Browse for the cs2.exe file.")

        autodetect_button = ttk.Button(path_frame, text="Autodetect", command=self.auto_detect_cs2_path)
        autodetect_button.grid(row=0, column=2, padx=5, pady=5)
        ToolTip(autodetect_button, "Attempt to automatically detect the CS2 server path.")

        # Server configuration options
        config_frame = ttk.LabelFrame(self.master, text="Server Configuration")
        config_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)
        self.master.grid_rowconfigure(1, weight=1) # Allow config frame to expand vertically

        # Left column for basic settings
        left_config_frame = ttk.Frame(config_frame)
        left_config_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Map selection
        ttk.Label(left_config_frame, text="Map:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.map_var = tk.StringVar(self.master)
        self.map_dropdown = ttk.OptionMenu(left_config_frame, self.map_var, "de_dust2", "de_dust2", "de_inferno", "de_nuke", "de_ancient", "de_vertigo", "de_mirage", "de_overpass")
        self.map_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.map_dropdown, "Select the map to load on server start.")

        # Game mode selection
        ttk.Label(left_config_frame, text="Game Mode:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.gamemode_var = tk.StringVar(self.master)
        self.gamemode_dropdown = ttk.OptionMenu(left_config_frame, self.gamemode_var, "Competitive", "Competitive", "Casual", "Deathmatch")
        self.gamemode_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.gamemode_dropdown, "Select the game mode for the server.")

        # Max Players
        ttk.Label(left_config_frame, text="Max Players:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.max_players_entry = ttk.Entry(left_config_frame, width=10)
        self.max_players_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.max_players_entry.insert(0, "10")
        ToolTip(self.max_players_entry, "Set the maximum number of players allowed on the server.")

        # Port
        ttk.Label(left_config_frame, text="Port:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.port_entry = ttk.Entry(left_config_frame, width=10)
        self.port_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.port_entry.insert(0, "27015")
        ToolTip(self.port_entry, "Set the port for the server. Default is 27015.")

        # RCON Password
        ttk.Label(left_config_frame, text="RCON Password:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.rcon_password_entry = ttk.Entry(left_config_frame, width=30, show="*")
        self.rcon_password_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(self.rcon_password_entry, "Set the RCON password for remote server administration.")

        # Server Name
        ttk.Label(left_config_frame, text="Server Name:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.server_name_entry = ttk.Entry(left_config_frame, width=30)
        self.server_name_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        self.server_name_entry.insert(0, "My CS2 Server")
        ToolTip(self.server_name_entry, "Set the name of your server as it appears in the server browser.")

        # Right column for advanced settings (initially empty, can be expanded)
        right_config_frame = ttk.Frame(config_frame)
        right_config_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        config_frame.grid_columnconfigure(1, weight=1) # Allow right column to expand

        ttk.Label(right_config_frame, text="Additional Command Line Arguments:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.additional_args_entry = ttk.Entry(right_config_frame, width=50)
        self.additional_args_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew", columnspan=2)
        ToolTip(self.additional_args_entry, "Add any extra command line arguments for the server.")
        right_config_frame.grid_columnconfigure(0, weight=1)

        # Server control buttons
        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew", columnspan=2)

        self.start_button = ttk.Button(button_frame, text="Start Server", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.X)
        self.stop_button = ttk.Button(button_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.X)

        # Log output
        log_frame = ttk.LabelFrame(self.master, text="Server Output Log")
        log_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)
        self.master.grid_rowconfigure(3, weight=2) # Log frame takes more vertical space

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, state=tk.DISABLED, height=15)
        self.log_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.log_text_scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=self.log_text_scrollbar.set)

        # Menu Bar
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)

        # File Menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Configuration", command=self.load_config)
        file_menu.add_command(label="Save Configuration", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Theme Menu
        theme_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Theme", menu=theme_menu)

        self.preset_theme_menu = tk.Menu(theme_menu, tearoff=0)
        theme_menu.add_cascade(label="Presets", menu=self.preset_theme_menu)
        self.update_preset_theme_menu() # Populate with initial presets

        theme_menu.add_command(label="Customize Theme", command=self.open_theme_customizer)
        theme_menu.add_command(label="Save Current Theme as Preset", command=self.save_current_theme_as_preset)
        theme_menu.add_command(label="Delete Theme Preset", command=self.delete_theme_preset)
        theme_menu.add_separator()
        theme_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)

    def update_preset_theme_menu(self):
        self.preset_theme_menu.delete(0, tk.END) # Clear existing items
        # Add default presets
        self.preset_theme_menu.add_command(label="Default Light", command=lambda: self.apply_preset_theme("Default Light"))
        self.preset_theme_menu.add_command(label="Default Dark", command=lambda: self.apply_preset_theme("Default Dark"))
        self.preset_theme_menu.add_separator()

        # Load custom presets from file
        self.load_custom_presets()
        if self.custom_presets:
            for preset_name in self.custom_presets.keys():
                self.preset_theme_menu.add_command(label=preset_name, command=lambda name=preset_name: self.apply_preset_theme(name))
        else:
            self.preset_theme_menu.add_command(label="No Custom Presets", state=tk.DISABLED)


    def toggle_dark_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme(self.is_dark_mode)
        self.append_to_log(f"Dark mode toggled to: {self.is_dark_mode}")


    def apply_theme(self, is_dark):
        self.is_dark_mode = is_dark
        if self.is_dark_mode:
            self.current_theme_colors = self.default_dark_theme_colors.copy()
            self.current_theme_colors.update(self.custom_colors.get("dark", {}))
            self.current_preset_name = "Default Dark" # Update preset name
        else:
            self.current_theme_colors = self.default_light_theme_colors.copy()
            self.current_theme_colors.update(self.custom_colors.get("light", {}))
            self.current_preset_name = "Default Light" # Update preset name


        # Apply colors to widgets
        self.master.config(bg=self.current_theme_colors["bg"])
        
        # Apply to all ttk widgets
        style = ttk.Style()
        style.theme_use('clam') # Use 'clam' or 'alt' for more theme control

        style.configure(".",
                        background=self.current_theme_colors["bg"],
                        foreground=self.current_theme_colors["fg"],
                        font=("Segoe UI", 9)
                        )
        style.configure("TFrame",
                        background=self.current_theme_colors["frame_bg"],
                        foreground=self.current_theme_colors["frame_fg"]
                        )
        style.configure("TLabelframe",
                        background=self.current_theme_colors["frame_bg"],
                        foreground=self.current_theme_colors["frame_fg"]
                        )
        style.configure("TLabelframe.Label",
                        background=self.current_theme_colors["frame_bg"],
                        foreground=self.current_theme_colors["frame_fg"]
                        )
        style.configure("TButton",
                        background=self.current_theme_colors["button_bg"],
                        foreground=self.current_theme_colors["button_fg"],
                        relief="flat"
                        )
        style.map("TButton",
                  background=[("active", self.current_theme_colors["active_button_bg"])],
                  foreground=[("active", self.current_theme_colors["active_button_fg"])]
                  )
        style.configure("TEntry",
                        fieldbackground=self.current_theme_colors["entry_bg"],
                        foreground=self.current_theme_colors["entry_fg"]
                        )
        style.configure("TText", # This won't work directly for tk.Text
                        background=self.current_theme_colors["log_bg"],
                        foreground=self.current_theme_colors["log_fg"]
                        )
        style.configure("TScrollbar",
                        background=self.current_theme_colors["pb_trough_bg"],
                        troughcolor=self.current_theme_colors["pb_trough_bg"],
                        relief="flat"
                        )
        style.map("TScrollbar",
                  background=[("active", self.current_theme_colors["active_button_bg"])]
                  )
        style.configure("Horizontal.TProgressbar",
                        background=self.current_theme_colors["pb_chunk_bg"],
                        troughcolor=self.current_theme_colors["pb_trough_bg"]
                        )
        style.configure("TLabel",
                        background=self.current_theme_colors["bg"],
                        foreground=self.current_theme_colors["fg"]
                        )
        
        # OptionMenu styling (ttk.OptionMenu uses TCombobox style in recent Tk versions or TMenubutton)
        style.configure("TMenubutton",
                        background=self.current_theme_colors["dropdown_bg"],
                        foreground=self.current_theme_colors["dropdown_fg"],
                        fieldbackground=self.current_theme_colors["dropdown_bg"] # This is often the actual clickable area
                        )
        style.map("TMenubutton",
                  background=[("active", self.current_theme_colors["dropdown_active_bg"])],
                  foreground=[("active", self.current_theme_colors["dropdown_active_fg"])]
                  )
        
        # Apply to tk.Text widget separately
        self.log_text.config(bg=self.current_theme_colors["log_bg"], fg=self.current_theme_colors["log_fg"], insertbackground=self.current_theme_colors["entry_fg"]) # insertbackground changes caret color

        # Update ToolTip colors (if they were already created)
        # This requires iterating through widgets or modifying the ToolTip class to re-apply themes
        # For simplicity, we assume tooltips are created after theme is somewhat set, or re-created.
        # A more robust solution would involve a theme-manager for tooltips.
        # For now, we'll ensure the default tooltip colors are updated based on the theme.
        ToolTip.background_color = self.current_theme_colors["tooltip_bg"]
        ToolTip.foreground_color = self.current_theme_colors["tooltip_fg"]


    def open_theme_customizer(self):
        customizer_window = tk.Toplevel(self.master)
        customizer_window.title("Customize Theme")
        customizer_window.transient(self.master) # Make it appear on top of the main window
        customizer_window.grab_set() # Disable interaction with the main window

        color_options = [
            ("Background:", "bg"), ("Foreground:", "fg"),
            ("Frame Background:", "frame_bg"), ("Frame Foreground:", "frame_fg"),
            ("Entry Background:", "entry_bg"), ("Entry Foreground:", "entry_fg"),
            ("Button Background:", "button_bg"), ("Button Foreground:", "button_fg"),
            ("Active Button Background:", "active_button_bg"), ("Active Button Foreground:", "active_button_fg"),
            ("Log Background:", "log_bg"), ("Log Foreground:", "log_fg"),
            ("Progressbar Trough:", "pb_trough_bg"), ("Progressbar Chunk:", "pb_chunk_bg"),
            ("Tooltip Background:", "tooltip_bg"), ("Tooltip Foreground:", "tooltip_fg"),
            ("Dropdown Background:", "dropdown_bg"), ("Dropdown Foreground:", "dropdown_fg"),
            ("Dropdown Active Background:", "dropdown_active_bg"), ("Dropdown Active Foreground:", "dropdown_active_fg"),
        ]

        row = 0
        for label_text, color_key in color_options:
            tk.Label(customizer_window, text=label_text, bg=self.current_theme_colors["bg"], fg=self.current_theme_colors["fg"]).grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            current_color = self.custom_colors.get("dark" if self.is_dark_mode else "light", {}).get(color_key, self.current_theme_colors.get(color_key, "#FFFFFF"))
            
            color_display = tk.Label(customizer_window, bg=current_color, width=8, relief="solid", borderwidth=1)
            color_display.grid(row=row, column=1, padx=5, pady=2, sticky="ew")

            choose_button = ttk.Button(customizer_window, text="Choose", 
                                        command=lambda kc=color_key, cd=color_display: self.choose_color(kc, cd))
            choose_button.grid(row=row, column=2, padx=5, pady=2)
            row += 1
        
        save_button = ttk.Button(customizer_window, text="Apply Custom Theme", command=self.apply_custom_theme)
        save_button.grid(row=row, column=0, columnspan=3, pady=10)

        # Apply current theme to the customizer window itself
        customizer_window.config(bg=self.current_theme_colors["bg"])
        for child in customizer_window.winfo_children():
            if isinstance(child, (tk.Label, ttk.Label, tk.Button, ttk.Button)):
                child.config(bg=self.current_theme_colors["bg"], fg=self.current_theme_colors["fg"])
            # Special handling for ttk buttons to ensure their style is applied
            if isinstance(child, ttk.Button):
                style = ttk.Style()
                style.map("TButton",
                          background=[("active", self.current_theme_colors["active_button_bg"])],
                          foreground=[("active", self.current_theme_colors["active_button_fg"])]
                          )


    def choose_color(self, color_key, color_display_widget):
        initial_color = color_display_widget.cget("bg")
        color_code = colorchooser.askcolor(initialcolor=initial_color)[1]
        if color_code:
            color_display_widget.config(bg=color_code)
            if self.is_dark_mode:
                self.custom_colors.setdefault("dark", {})[color_key] = color_code
            else:
                self.custom_colors.setdefault("light", {})[color_key] = color_code
            self.apply_theme(self.is_dark_mode) # Apply immediately to see changes


    def apply_custom_theme(self):
        # This function is called when "Apply Custom Theme" is clicked in the customizer
        # The self.custom_colors dictionary is already updated by choose_color
        self.apply_theme(self.is_dark_mode)
        self.append_to_log("Custom theme applied.")
        messagebox.showinfo("Theme Customizer", "Custom theme applied successfully!")

    def save_current_theme_as_preset(self):
        preset_name = tk.simpledialog.askstring("Save Theme Preset", "Enter a name for the new theme preset:")
        if preset_name:
            if preset_name in self.custom_presets:
                if not messagebox.askyesno("Overwrite Preset", f"Preset '{preset_name}' already exists. Do you want to overwrite it?"):
                    return

            theme_data = {
                "is_dark_mode": self.is_dark_mode,
                "colors": self.current_theme_colors # Save the currently active colors
            }
            if self.custom_colors.get("light") or self.custom_colors.get("dark"):
                theme_data["custom_colors"] = self.custom_colors # Save custom modifications if any

            self.custom_presets[preset_name] = theme_data
            self.save_custom_presets()
            self.update_preset_theme_menu()
            self.append_to_log(f"Theme preset '{preset_name}' saved.")
            messagebox.showinfo("Save Preset", f"Theme preset '{preset_name}' saved successfully!")

    def load_custom_presets(self):
        try:
            with open("theme_presets.json", "r") as f:
                self.custom_presets = json.load(f)
        except FileNotFoundError:
            self.custom_presets = {}
        except json.JSONDecodeError as e:
            self.append_to_log(f"Error decoding theme_presets.json: {e}")
            self.custom_presets = {}

    def save_custom_presets(self):
        with open("theme_presets.json", "w") as f:
            json.dump(self.custom_presets, f, indent=4)

    def apply_preset_theme(self, preset_name=None):
        if preset_name == "Default Light":
            self.is_dark_mode = False
            self.custom_colors = {"light": {}, "dark": {}} # Clear custom colors
            self.apply_theme(False)
            self.current_preset_name = "Default Light"
            self.append_to_log("Applied 'Default Light' theme preset.")
        elif preset_name == "Default Dark":
            self.is_dark_mode = True
            self.custom_colors = {"light": {}, "dark": {}} # Clear custom colors
            self.apply_theme(True)
            self.current_preset_name = "Default Dark"
            self.append_to_log("Applied 'Default Dark' theme preset.")
        elif preset_name and preset_name in self.custom_presets:
            preset_data = self.custom_presets[preset_name]
            self.is_dark_mode = preset_data.get("is_dark_mode", False)
            # Load colors from the preset. If custom_colors were saved, use them.
            # Otherwise, reset custom_colors for the current mode.
            if "custom_colors" in preset_data:
                self.custom_colors = preset_data["custom_colors"].copy()
            else:
                self.custom_colors = {"light": {}, "dark": {}} # No custom colors saved in this preset

            self.apply_theme(self.is_dark_mode) # Apply the base theme
            
            # Now, explicitly apply the saved colors from the preset, overwriting defaults if needed.
            # This ensures that even if custom_colors were not explicitly saved, the exact colors of the preset are restored.
            if "colors" in preset_data:
                # The 'colors' key in preset_data should contain the final resolved colors when it was saved.
                # We can apply these directly, or merge them. For simplicity and correctness in restoring,
                # we'll update the current_theme_colors with these values and then re-apply.
                if self.is_dark_mode:
                    self.current_theme_colors.update(preset_data["colors"])
                else:
                    self.current_theme_colors.update(preset_data["colors"])
                self.apply_theme(self.is_dark_mode) # Re-apply to ensure all widgets get the exact saved colors

            self.current_preset_name = preset_name
            self.append_to_log(f"Applied theme preset: '{preset_name}'.")
        else:
            # Fallback for when no preset name is provided or it's not found
            # This might happen on initial load if config specifies an unknown preset
            self.apply_theme(self.is_dark_mode)
            self.append_to_log(f"Applied default theme (Dark Mode: {self.is_dark_mode}).")


    def delete_theme_preset(self):
        if not self.custom_presets:
            messagebox.showinfo("Delete Preset", "No custom presets to delete.")
            return

        preset_names = list(self.custom_presets.keys())
        # Create a simple dialog for selection
        dialog = tk.Toplevel(self.master)
        dialog.title("Delete Theme Preset")
        dialog.transient(self.master)
        dialog.grab_set()

        tk.Label(dialog, text="Select preset to delete:").pack(pady=10)
        
        listbox_frame = ttk.Frame(dialog)
        listbox_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(listbox_frame, height=len(preset_names) if preset_names else 1)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        listbox.config(yscrollcommand=scrollbar.set)

        for name in preset_names:
            listbox.insert(tk.END, name)

        def confirm_delete():
            selected_indices = listbox.curselection()
            if selected_indices:
                selected_preset_name = listbox.get(selected_indices[0])
                if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the preset '{selected_preset_name}'?"):
                    del self.custom_presets[selected_preset_name]
                    self.save_custom_presets()
                    self.update_preset_theme_menu()
                    self.append_to_log(f"Theme preset '{selected_preset_name}' deleted.")
                    messagebox.showinfo("Delete Preset", f"Preset '{selected_preset_name}' deleted successfully!")
                    dialog.destroy()
            else:
                messagebox.showwarning("No Selection", "Please select a preset to delete.")

        ttk.Button(dialog, text="Delete Selected", command=confirm_delete).pack(pady=10)
        dialog.wait_window() # Wait for the dialog to close


    def append_to_log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def browse_path(self):
        # Allow user to select the cs2.exe file directly
        filepath = filedialog.askopenfilename(
            title="Select cs2.exe",
            filetypes=[("CS2 Executable", "cs2.exe")]
        )
        if filepath:
            # Check if the selected path is indeed cs2.exe in the expected directory structure
            # e.g., .../Steam/steamapps/common/Counter-Strike Global Offensive/game/bin/win64/cs2.exe
            expected_tail = os.path.join("game", "bin", "win64", "cs2.exe")
            if expected_tail in filepath:
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, filepath)
                self.append_to_log(f"CS2 path set to: {filepath}")
            else:
                messagebox.showwarning("Invalid Path", "Please select the 'cs2.exe' file located in '...Counter-Strike Global Offensive\\game\\bin\\win64\\'.")
                self.append_to_log(f"Invalid path selected: {filepath}")

    def auto_detect_cs2_path(self):
        self.append_to_log("Attempting to autodetect CS2 path...")
        try:
            cs2_path = auto_detect_cs2_path(log_callback=self.append_to_log)
            if cs2_path:
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, cs2_path)
                self.append_to_log(f"Autodetected CS2 path: {cs2_path}")
            else:
                messagebox.showwarning("Autodetect Failed", "Could not automatically detect CS2 path. Please browse manually.")
                self.append_to_log("CS2 path autodetect failed.")
        except Exception as e:
            messagebox.showerror("Autodetect Error", f"An error occurred during autodetect: {e}")
            self.append_to_log(f"Error during autodetect: {e}")


    def start_server(self):
        cs2_exe_path = self.path_entry.get()
        if not cs2_exe_path or not os.path.exists(cs2_exe_path):
            messagebox.showerror("Error", "Invalid CS2 server executable path.")
            self.append_to_log("Error: Invalid CS2 server executable path.")
            return

        if self.server_process and self.server_process.poll() is None:
            messagebox.showinfo("Info", "Server is already running.")
            self.append_to_log("Server is already running.")
            return

        # Construct command
        # Example: C:\Steam\steamapps\common\Counter-Strike Global Offensive\game\bin\win64\cs2.exe -dedicated -console +map de_dust2 +game_type 0 +game_mode 1
        
        # Determine the correct server start command based on known patterns
        # For CS2, it's typically 'cs2.exe -dedicated'
        server_dir = os.path.dirname(cs2_exe_path)
        game_dir = os.path.dirname(server_dir) # Should be '...\game\bin\win64' -> '...\game'
        csgo_dir = os.path.dirname(game_dir) # Should be '...\Counter-Strike Global Offensive'

        # This is important: The dedicated server needs to be run from the CSGO root directory
        # where the 'game' folder resides.
        
        map_name = self.map_var.get()
        game_mode = self.gamemode_dropdown.get()
        max_players = self.max_players_entry.get()
        port = self.port_entry.get()
        rcon_password = self.rcon_password_entry.get()
        server_name = self.server_name_entry.get()
        additional_args = self.additional_args_entry.get()

        # Map game mode string to type and mode numbers
        game_type = 0 # Classic
        game_mode_num = 1 # Competitive
        if game_mode == "Casual":
            game_type = 0
            game_mode_num = 0
        elif game_mode == "Deathmatch":
            game_type = 1
            game_mode_num = 2
        elif game_mode == "Arms Race":
            game_type = 1
            game_mode_num = 0

        command = [
            cs2_exe_path,
            "-dedicated",
            "-console",
            f"+map {map_name}",
            f"+game_type {game_type}",
            f"+game_mode {game_mode_num}",
            f"+maxplayers {max_players}",
            f"+ip {detect_ip_address(self.append_to_log)}", # Auto-detect IP
            f"-port {port}"
        ]

        if rcon_password:
            command.append(f"+rcon_password {shlex.quote(rcon_password)}") # Use shlex.quote for safety
        if server_name:
            # server_name_escaped = shlex.quote(server_name) # Server name might not need quoting depending on server parsing
            command.append(f'+hostname "{server_name}"') # Use quotes for server name
        if additional_args:
            command.extend(shlex.split(additional_args)) # Split additional args safely

        try:
            self.append_to_log(f"Starting server with command: {' '.join(command)}")
            # Use preexec_fn=os.setsid to create a new process group on Unix-like systems
            # This makes it easier to terminate the process and its children.
            # For Windows, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP serves a similar purpose.
            
            # Change working directory to the CSGO root for the server process
            self.server_process = subprocess.Popen(
                command,
                cwd=csgo_dir, # Set the working directory
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Redirect stderr to stdout
                text=True, # Decode stdout/stderr as text
                bufsize=1, # Line-buffered
                universal_newlines=True, # Handle different line endings
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0 # For Windows
            )
            self.stop_log_thread.clear()
            self.output_log_thread = threading.Thread(target=self.read_output, daemon=True)
            self.output_log_thread.start()

            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            messagebox.showinfo("Server Control", "Server started successfully!")
            self.append_to_log("Server process initiated.")

        except FileNotFoundError:
            messagebox.showerror("Error", "CS2 executable not found. Check path.")
            self.append_to_log("Error: CS2 executable not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")
            self.append_to_log(f"Error starting server: {e}")

    def read_output(self):
        for line in iter(self.server_process.stdout.readline, ''):
            if self.stop_log_thread.is_set():
                break
            self.append_to_log(line.strip())
        self.server_process.stdout.close()
        self.append_to_log("Server output stream closed.")


    def stop_server(self):
        if self.server_process and self.server_process.poll() is None:
            self.append_to_log("Stopping server...")
            try:
                # Terminate the process group to ensure all child processes are stopped
                if os.name == 'nt':
                    # On Windows, use taskkill with /F (force) and /T (tree kill) on the process group ID
                    subprocess.run(f"taskkill /F /T /PID {self.server_process.pid}", shell=True, check=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    # On Unix-like systems, kill the process group
                    os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM) # SIGTERM for graceful shutdown
                    time.sleep(1) # Give it a moment
                    if self.server_process.poll() is None: # If still running, force kill
                        os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)


                self.stop_log_thread.set() # Signal the log reading thread to stop
                if self.output_log_thread and self.output_log_thread.is_alive():
                    self.output_log_thread.join(timeout=5) # Wait for thread to finish

                self.server_process.wait(timeout=5) # Wait for process to terminate
                self.append_to_log("Server stopped.")
                messagebox.showinfo("Server Control", "Server stopped successfully.")

            except Exception as e:
                self.append_to_log(f"Error stopping server: {e}")
                messagebox.showerror("Error", f"Failed to stop server: {e}")
            finally:
                self.server_process = None
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
        else:
            self.append_to_log("No server is currently running.")
            messagebox.showinfo("Info", "No server is currently running.")


    def save_config(self):
        config_data = {
            "cs2_path": self.path_entry.get(),
            "map": self.map_var.get(),
            "gamemode": self.gamemode_var.get(),
            "max_players": self.max_players_entry.get(),
            "port": self.port_entry.get(),
            "rcon_password": self.rcon_password_entry.get(),
            "server_name": self.server_name_entry.get(),
            "additional_args": self.additional_args_entry.get(),
            "is_dark_mode": self.is_dark_mode,
            "custom_colors": self.custom_colors, # Save custom colors
            "current_preset_name": self.current_preset_name # Save the name of the active preset
        }
        filepath = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON files", "*.json")],
                                                title="Save Configuration As")
        if filepath:
            try:
                with open(filepath, "w") as f:
                    json.dump(config_data, f, indent=4)
                self.append_to_log(f"Configuration saved to: {filepath}")
                messagebox.showinfo("Save Config", "Configuration saved successfully!")
            except Exception as e:
                self.append_to_log(f"Error saving configuration: {e}")
                messagebox.showerror("Save Config Error", f"Failed to save configuration: {e}")

    def load_config(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")],
                                                title="Load Configuration From")
        if filepath:
            try:
                with open(filepath, "r") as f:
                    config_data = json.load(f)

                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, config_data.get("cs2_path", ""))
                self.map_var.set(config_data.get("map", "de_dust2"))
                self.gamemode_var.set(config_data.get("gamemode", "Competitive"))
                self.max_players_entry.delete(0, tk.END)
                self.max_players_entry.insert(0, config_data.get("max_players", "10"))
                self.port_entry.delete(0, tk.END)
                self.port_entry.insert(0, config_data.get("port", "27015"))
                self.rcon_password_entry.delete(0, tk.END)
                self.rcon_password_entry.insert(0, config_data.get("rcon_password", ""))
                self.server_name_entry.delete(0, tk.END)
                self.server_name_entry.insert(0, config_data.get("server_name", "My CS2 Server"))
                self.additional_args_entry.delete(0, tk.END)
                self.additional_args_entry.insert(0, config_data.get("additional_args", ""))

                # Load theme preference and custom colors
                loaded_is_dark = config_data.get("is_dark_mode", False)
                loaded_custom_colors = config_data.get("custom_colors", {"light": {}, "dark": {}})
                loaded_preset_name = config_data.get("current_preset_name", None)

                self.custom_colors = loaded_custom_colors # Set loaded custom colors

                if loaded_preset_name:
                    # If a specific preset name was saved, try to apply it.
                    # This will handle both default and custom presets.
                    self.apply_preset_theme(loaded_preset_name)
                else:
                    # Otherwise, apply the theme based on the loaded is_dark_mode flag,
                    # which will also incorporate any loaded custom_colors for that mode.
                    self.apply_theme(loaded_is_dark) 

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