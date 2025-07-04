import tkinter as tk

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