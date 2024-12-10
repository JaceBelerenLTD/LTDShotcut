import os
from tkinter import filedialog

class FileLoader:
    def load_image(self, initialdir="."):
        return filedialog.askopenfilename(
            initialdir=initialdir,
            title="Select an Image File",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All Files", "*.*")]
        )

    def load_video(self, initialdir="."):
        return filedialog.askopenfilename(
            initialdir=initialdir,
            title="Select a Video File",
            filetypes=[("Video Files", "*.mp4;*.avi;*.mkv;*.mov"), ("All Files", "*.*")]
        )

    def load_shortcut(self, initialdir="."):
        return filedialog.askopenfilename(
            initialdir=initialdir,
            title="Select a Shortcut File",
            filetypes=[("Shortcut Files", "*.mlt;*.xml"), ("All Files", "*.*")]
        )
