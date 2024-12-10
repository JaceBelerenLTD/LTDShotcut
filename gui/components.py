from tkinter import filedialog
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import os
import xml.etree.ElementTree as ET

class ImageViewer:
    def __init__(self, parent):
        self.label = tk.Label(parent, text="Image Viewer")
        self.label.pack()
        self.image_label = tk.Label(parent)
        self.image_label.pack()

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            img = Image.open(file_path)
            from PIL import Image
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk


class VideoPlayer:
    def __init__(self, parent):
        self.label = tk.Label(parent, text="Video Player")
        self.label.pack()

    def load_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi")])
        if file_path:
            # Placeholder for video player logic (can use OpenCV)
            self.label.config(text=f"Selected Video: {os.path.basename(file_path)}")