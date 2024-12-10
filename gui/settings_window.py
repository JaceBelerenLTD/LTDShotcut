from tkinter import ttk
import tkinter as tk

class SettingsWindow:
    """
    SettingsWindow provides a menu for adjusting application settings, such as changing the background image or edge color.
    """
    def __init__(self, root, apply_settings_callback):
        """
        Initialize the settings window.

        Args:
            root (Tk): The parent Tkinter root window.
            apply_settings_callback (function): Callback function to apply changes (e.g., update the edge color).
        """
        self.root = tk.Toplevel(root)  # Create a new top-level window
        self.root.title("Settings")
        self.root.geometry("400x300")

        self.apply_settings_callback = apply_settings_callback

        # Edge color adjustment
        ttk.Label(self.root, text="Edge Color (Hex):").pack(pady=10)
        self.edge_color_entry = ttk.Entry(self.root)
        self.edge_color_entry.insert(0, "#000000")  # Default to black
        self.edge_color_entry.pack(pady=10)

        # Apply button
        self.apply_button = ttk.Button(self.root, text="Apply", command=self.apply_changes)
        self.apply_button.pack(pady=10)

    def apply_changes(self):
        """
        Applies the selected settings (e.g., edge color).
        """
        new_edge_color = self.edge_color_entry.get()
        self.apply_settings_callback(new_edge_color)
        self.root.destroy()  # Close the settings window
