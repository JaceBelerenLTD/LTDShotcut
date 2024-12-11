from tkinter import ttk, filedialog
import tkinter as tk
import os
import json  # To handle configuration file reading and writing
from resources.styles import IMAGES_PATH
class SettingsWindow:
    def __init__(self, parent, current_background_image, save_callback):
        self.parent = parent
        self.current_background_image = current_background_image
        self.save_callback = save_callback

        # Create the settings window
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("400x300")

        # Background image selection
        tk.Label(self.window, text="Select Background Image:", font=("Arial", 12)).pack(pady=5)
        self.image_var = tk.StringVar(value=self.current_background_image)
        self.image_options = self.get_available_images()
        self.image_dropdown = ttk.Combobox(self.window, textvariable=self.image_var, values=self.image_options, state="readonly")
        self.image_dropdown.pack(pady=10)

        # Export folder selection
        tk.Label(self.window, text="Select Export Folder:", font=("Arial", 12)).pack(pady=5)
        self.export_folder_var = tk.StringVar(value=self.get_export_folder())  # Load saved folder
        self.export_folder_entry = ttk.Entry(self.window, textvariable=self.export_folder_var, width=50, state="readonly")
        self.export_folder_entry.pack(pady=10)
        ttk.Button(self.window, text="Choose Folder", command=self.select_export_folder).pack(pady=10)

        # Save button
        ttk.Button(self.window, text="Save", command=self.save_settings).pack(pady=20)

    def get_available_images(self):
        """Get the list of available images."""
        if os.path.exists(IMAGES_PATH):
            return [f for f in os.listdir(IMAGES_PATH) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        return []

    def get_export_folder(self):
        """Retrieve the export folder from settings."""
        config_file = "config.json"
        if os.path.exists(config_file):
            with open(config_file, "r") as file:
                config = json.load(file)
            return config.get("export_folder", "")
        return ""

    def select_export_folder(self):
        """Open a dialog to select the export folder."""
        folder = filedialog.askdirectory(title="Select Export Folder")
        if folder:
            self.export_folder_var.set(folder)

    def save_settings(self):
        """Save settings including the export folder."""
        config_file = "config.json"
        with open(config_file, "r") as file:
            config = json.load(file) if os.path.exists(config_file) else {}

        # Update the export folder
        config["export_folder"] = self.export_folder_var.get()

        # Save the updated config
        with open(config_file, "w") as file:
            json.dump(config, file, indent=4)

        # Save background image if applicable
        selected_image = self.image_var.get()
        if selected_image:  
            selected_image_path = os.path.join(IMAGES_PATH, selected_image)
            self.save_callback(selected_image_path)

        self.window.destroy()
