from tkinter import ttk
import tkinter as tk
import os
from resources.styles import IMAGES_PATH


class SettingsWindow:
    def __init__(self, parent, current_background_image, save_callback):
        
        self.parent = parent
        self.current_background_image = current_background_image
        self.save_callback = save_callback

        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("400x300")

        # Background image selection dropdown
        tk.Label(self.window, text="Select Background Image:", font=("Arial", 12)).pack(pady=10)
        self.image_var = tk.StringVar(value=self.current_background_image)

        # Populate dropdown menu with available images
        self.image_options = self.get_available_images()
        print("Available images:", self.image_options)  # Debugging
        self.image_dropdown = ttk.Combobox(self.window, textvariable=self.image_var, values=self.image_options, state="readonly")
        self.image_dropdown.pack(pady=10)

        # Save button
        ttk.Button(self.window, text="Save", command=self.save_settings).pack(pady=20)

    def get_available_images(self):
        """Get the list of available images in the resources/images directory."""
        if os.path.exists(IMAGES_PATH):
            return [f for f in os.listdir(IMAGES_PATH) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        return []

    def save_settings(self):
        selected_image = self.image_var.get()
        if selected_image:  # Construct the full path using IMAGES_PATH
            selected_image_path = os.path.join(IMAGES_PATH, selected_image)
            self.save_callback(selected_image_path)
        self.window.destroy()