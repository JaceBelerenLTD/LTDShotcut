from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
import os

class MainWindow:
    def __init__(self, root):
        """
        MainWindow constructor that sets up the main application layout.
        """
        self.root = root
        self.root.title("Media Display App")

        # Path to the background image
        bg_image_path = "resources/images/BackgroundLTDLoadScreen.png"

        # Background image and edge color
        self.edge_color = "#000000"  # Default black edge color
        self.bg_image = None  # Initialize bg_image as None

        # Try loading the background image
        if os.path.exists(bg_image_path):
            try:
                self.bg_image = Image.open(bg_image_path)
            except Exception as e:
                print(f"Error loading background image: {e}")
        else:
            print(f"Background image not found: {bg_image_path}")
            self.bg_image = None

        # Create Canvas for the background
        self.background = tk.Canvas(root)
        self.background.pack(fill="both", expand=True)

        # Resize the background immediately
        self.resize_background(None)

        # Lower the background to ensure buttons are visible
        self.background.lower("all")

        # Create frames for widgets
        self.image_frame = ttk.Frame(self.root)
        self.video_frame = ttk.Frame(self.root)
        self.text_frame = ttk.Frame(self.root)
        self.controls_frame = ttk.Frame(self.root)

        # Place the frames using Canvas.create_window
        self.background.create_window(100, 100, window=self.image_frame, anchor="nw")
        self.background.create_window(400, 100, window=self.video_frame, anchor="nw")
        self.background.create_window(100, 300, window=self.text_frame, anchor="nw")
        self.background.create_window(400, 300, window=self.controls_frame, anchor="nw")

        # Add action buttons
        self.load_image_button = ttk.Button(self.controls_frame, text="Load Image", command=lambda: print("Load Image clicked"))
        self.load_video_button = ttk.Button(self.controls_frame, text="Load Video", command=lambda: print("Load Video clicked"))
        self.load_shotcut_button = ttk.Button(self.controls_frame, text="Load Shotcut File", command=lambda: print("Load Shotcut clicked"))
        self.settings_button = ttk.Button(self.controls_frame, text="Settings", command=lambda: print("Settings clicked"))

        # Pack buttons in the controls_frame
        self.load_image_button.pack(pady=5)
        self.load_video_button.pack(pady=5)
        self.load_shotcut_button.pack(pady=5)
        self.settings_button.pack(pady=5)

        # Bind resize event after initializing components
        self.root.bind("<Configure>", self.resize_background)

    def resize_background(self, event):
        """
        Resizes the background image to fit the window while maintaining its aspect ratio.
        Colors uncovered edges with the specified edge color.
        """
        canvas_width = self.root.winfo_width()
        canvas_height = self.root.winfo_height()

        # Clear the canvas
        self.background.delete("all")

        if self.bg_image:
            # Calculate aspect ratio
            img_aspect = self.bg_image.width / self.bg_image.height
            canvas_aspect = canvas_width / canvas_height

            # Scale image while keeping aspect ratio
            if canvas_aspect > img_aspect:
                new_width = canvas_width
                new_height = int(new_width / img_aspect)
            else:
                new_height = canvas_height
                new_width = int(new_height * img_aspect)

            resized_image = self.bg_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized_image)

            # Draw the background image
            self.background.create_image(canvas_width // 2, canvas_height // 2, image=self.bg_photo, anchor="center")
        else:
            # Draw a solid color background if no image is available
            self.background.create_rectangle(0, 0, canvas_width, canvas_height, fill=self.edge_color, outline="")
