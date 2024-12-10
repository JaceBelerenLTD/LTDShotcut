from tkinter import ttk
import tkinter as tk
from resources.styles import BACKGROUND_IMAGE_PATH, BACKGROUND_IMAGE_OPTION_2

class SettingsWindow:
    """
    SettingsWindow provides a menu for adjusting application settings, such as changing the background image.
    """
    def __init__(self, root, apply_changes_callback):
        """
        Initialize the settings window.

        Args:
            root (Tk): The parent Tkinter root window.
            apply_changes_callback (function): Callback function to apply changes (e.g., update the background).
        """
        self.root = tk.Toplevel(root)  # Create a new top-level window
        self.root.title("Settings")
        self.root.geometry("400x300")

        self.apply_changes_callback = apply_changes_callback

        # Add a dropdown to select a background
        ttk.Label(self.root, text="Select Background:").pack(pady=10)
        self.background_options = {
            "Default": BACKGROUND_IMAGE_PATH,
            "Option 2": BACKGROUND_IMAGE_OPTION_2,
        }
        self.background_dropdown = ttk.Combobox(
            self.root, values=list(self.background_options.keys())
        )
        self.background_dropdown.set("Default")
        self.background_dropdown.pack(pady=10)

        # Add an Apply button
        self.apply_button = ttk.Button(self.root, text="Apply", command=self.apply_changes)
        self.apply_button.pack(pady=10)

    def apply_changes(self):
        """
        Applies the selected settings and updates the main application window.
        """
        selected_option = self.background_dropdown.get()
        if selected_option in self.background_options:
            new_bg_path = self.background_options[selected_option]
            self.apply_changes_callback(new_bg_path)
