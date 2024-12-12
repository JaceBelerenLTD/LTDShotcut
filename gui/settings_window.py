from tkinter import ttk, filedialog
import tkinter as tk
import os
import json  # To handle configuration file reading and writing
from resources.styles import IMAGES_PATH

class SettingsWindow:
    def __init__(self, parent, save_callback):
        self.parent = parent
        self.save_callback = save_callback
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("500x400")
        self.config_file = "config.json"

         # Fetch current settings from config.json
        self.config = self.load_config()
        self.current_background_image = self.config.get("background_image", "Not Set")
        self.current_export_folder = self.config.get("export_folder", "Not Set")

        # Build the settings UI (background image, export folder, etc.)
        self.build_ui()

    def build_ui(self):
        # Create grid layout
        self.grid = ttk.Frame(self.window)
        self.grid.pack(fill="both", expand=True, padx=10, pady=10)
        self.grid.columnconfigure(0, weight=1)
        self.grid.columnconfigure(1, weight=1)
        self.grid.columnconfigure(2, weight=2)

        # Add column headers
        ttk.Label(self.grid, text="Name", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(self.grid, text="Function", font=("Arial", 12, "bold")).grid(row=0, column=1, sticky="w")
        ttk.Label(self.grid, text="State", font=("Arial", 12, "bold")).grid(row=0, column=2, sticky="w")

        # Background Image
        ttk.Label(self.grid, text="Background Image:").grid(row=1, column=0, sticky="w", pady=5)
        self.image_var = tk.StringVar(value=os.path.basename(self.current_background_image) if self.current_background_image else "Not Set")
        self.image_dropdown = ttk.Combobox(self.grid, textvariable=self.image_var, values=self.get_available_images(), state="readonly")
        self.image_dropdown.grid(row=1, column=1, sticky="ew", pady=5)
        ttk.Label(self.grid, textvariable=self.image_var).grid(row=1, column=2, sticky="w", pady=5)

        # Export Folder
        ttk.Label(self.grid, text="Export Folder:").grid(row=2, column=0, sticky="w", pady=5)
        export_folder = self.get_export_folder()
        self.export_folder_var = tk.StringVar(value=export_folder if export_folder else "Not Set")
        self.export_button = ttk.Button(self.grid, text="Choose Folder", command=self.select_export_folder)
        self.export_button.grid(row=2, column=1, sticky="ew", pady=5)
        self.export_folder_label = ttk.Label(self.grid, textvariable=self.export_folder_var)
        self.export_folder_label.grid(row=2, column=2, sticky="w", pady=5)

        # Save button
        self.save_button = ttk.Button(self.window, text="Save", command=self.save_settings)
        self.save_button.pack(side="bottom", pady=10)

    def load_config(self):
        """Load the configuration from config.json."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                return json.load(file)
        return {}
    
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
            return config.get("export_folder", "Not Set")
        return "Not Set"

    def select_export_folder(self):
        """Open a dialog to select the export folder."""
        folder = filedialog.askdirectory(title="Select Export Folder")
        if folder:
            self.export_folder_var.set(folder)

    def save_settings(self):
        """Save changes to settings and update config.json."""
        # Load the existing configuration
        config_file = "config.json"
        config = {}

        if os.path.exists(config_file):
            with open(config_file, "r") as file:
                try:
                    config = json.load(file)
                except json.JSONDecodeError:
                    print("Debug: Error decoding JSON. Using empty config.")

        # Update config with new values
        selected_image = self.image_var.get()
        config["background_image"] = os.path.join(IMAGES_PATH, self.image_var.get())  # Save the selected background image
        config["export_folder"] = self.export_folder_var.get()  # Save the selected export folder

        # Save the updated configuration
        with open(config_file, "w") as file:
            json.dump(config, file, indent=4)

        self.save_callback(os.path.join(IMAGES_PATH, selected_image))

        # Close the settings window
        self.window.destroy()
