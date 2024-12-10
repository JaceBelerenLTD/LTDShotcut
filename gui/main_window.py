import json
import os
import cv2
from PIL import Image, ImageTk  # For displaying images
from tkinter import ttk
import tkinter as tk
from threading import Thread  # To handle video playback without freezing the GUI
from Services.file_loader import FileLoader
from Services.media_handler import MediaHandler
from gui.components import ImageViewer, VideoPlayer
from resources.styles import BACKGROUND_COLOR


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Display App")

        # Persistent configuration
        self.config_file = "config.json"
        self.last_opened_files = self.load_last_opened_files()
        self.background_image_path = self.last_opened_files.get("background_image", None)

        # Set the root window background
        self.background_label = ttk.Label(self.root)
        self.background_label.place(relwidth=1, relheight=1)

        # Load and set the background image
        self.background_image = None  # To store the loaded background image
        if self.background_image_path and os.path.exists(self.background_image_path):
            self.set_background_image(self.background_image_path)
        else:
            self.root.configure(bg=BACKGROUND_COLOR)
        
        # Set window size based on the image
        if self.background_image:
            self.adjust_window_to_image()

        # Initialize file and media handlers
        self.file_loader = FileLoader()
        self.media_handler = MediaHandler()

        # Variables for video playback
        self.video_thread = None
        self.stop_video_flag = False
        self.pause_video_flag = False
        self.current_video_path = None

        # Create frames
        self.image_frame = ttk.Frame(self.root, style="Blue.TFrame")
        self.video_frame = ttk.Frame(self.root, style="Blue.TFrame")
        self.text_frame = ttk.Frame(self.root, style="Blue.TFrame")
        self.controls_frame = ttk.Frame(self.root, style="Blue.TFrame")

        self.image_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.video_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.text_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.controls_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Define styles
        style = ttk.Style()
        style.configure("Blue.TFrame", background=BACKGROUND_COLOR)
        style.configure("Blue.TLabel", background=BACKGROUND_COLOR)
        style.configure("Blue.TButton", background=BACKGROUND_COLOR)

        # Image viewer
        self.image_viewer = ImageViewer(self.image_frame)
        self.image_label_widget = ttk.Label(self.image_frame, anchor="center", style="Blue.TLabel")
        self.image_label_widget.pack(fill="both", expand=True)

        # Video controls
        self.video_control_frame = ttk.Frame(self.video_frame, style="Blue.TLabel")
        self.video_control_frame.pack(fill="x", side="top", pady=5)

        self.video_display_frame = ttk.Frame(self.video_frame)
        self.video_display_frame.pack(fill="both", expand=True)

        self.play_button = ttk.Button(self.video_control_frame, text="Play", command=self.play_video_controls, style="Blue.TButton")
        self.play_button.pack(side="left", padx=5)
        self.pause_button = ttk.Button(self.video_control_frame, text="Pause", command=self.pause_video_controls, style="Blue.TButton")
        self.pause_button.pack(side="left", padx=5)
        self.stop_button = ttk.Button(self.video_control_frame, text="Stop", command=self.stop_video_controls, style="Blue.TButton")
        self.stop_button.pack(side="left", padx=5)

        self.video_label_widget = ttk.Label(self.video_display_frame, text="No video loaded", anchor="center", style="Blue.TLabel")
        self.video_label_widget.pack(fill="both", expand=True)

        # Marker tree
        self.file_label = ttk.Label(self.text_frame, text="File: No file loaded", font=("Arial", 12, "bold"), anchor="w")
        self.file_label.pack(fill="x", padx=5, pady=5)

        grid_frame = ttk.Frame(self.text_frame)
        grid_frame.pack(fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(grid_frame, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        self.marker_tree = ttk.Treeview(
            grid_frame,
            columns=("Number", "Name", "Time", "Picture", "Video"),
            show="headings",
            selectmode="browse",
            yscrollcommand=self.scrollbar.set
        )
        self.marker_tree.heading("Number", text="Nr.")
        self.marker_tree.heading("Name", text="Name")
        self.marker_tree.heading("Time", text="Time")
        self.marker_tree.heading("Picture", text="Picture")
        self.marker_tree.heading("Video", text="Video")
        self.marker_tree.pack(fill="both", expand=True)

        self.scrollbar.config(command=self.marker_tree.yview)

        self.marker_tree.column("Number", width=50, anchor="center")
        self.marker_tree.column("Name", width=150, anchor="w")
        self.marker_tree.column("Time", width=100, anchor="center")
        self.marker_tree.column("Picture", width=100, anchor="center")
        self.marker_tree.column("Video", width=100, anchor="center")

        # Controls buttons
        self.load_image_button = ttk.Button(self.controls_frame, text="Load Image", command=self.load_image)
        self.load_video_button = ttk.Button(self.controls_frame, text="Load Video", command=self.load_video)
        self.load_shotcut_button = ttk.Button(self.controls_frame, text="Load Shotcut File", command=self.load_shotcut)
        self.settings_button = ttk.Button(self.controls_frame, text="Settings", command=self.open_settings)

        self.load_image_button.pack(pady=5)
        self.load_video_button.pack(pady=5)
        self.load_shotcut_button.pack(pady=5)
        self.settings_button.pack(pady=5)

        # Auto-load markers
        self.auto_load_markers()

    def load_image(self):
        file_path = self.file_loader.load_image(initialdir=self.last_opened_files.get("image_folder", os.getcwd()))
        if not file_path:
            return
        self.last_opened_files["image"] = file_path
        self.last_opened_files["image_folder"] = os.path.dirname(file_path)
        self.save_last_opened_files()

        # Display image directly in image_label_widget
        image = Image.open(file_path)
        image = image.resize((self.image_frame.winfo_width(), self.image_frame.winfo_height()), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.image_label_widget.config(image=photo, text="")
        self.image_label_widget.image = photo
        
    def set_background_image(self, image_path):
        """Sets the background image from the given path."""
        try:
            self.background_image = Image.open(image_path)
            photo = ImageTk.PhotoImage(self.background_image)

            # Update the label with the image
            self.background_label.config(image=photo)
            self.background_label.image = photo
        except Exception as e:
            print(f"Error loading image: {e}")
            self.background_image = None
            self.background_label.config(image="", text="Background load failed")
    
    def adjust_window_to_image(self):
        """Adjusts the window size to match the background image dimensions."""
        if self.background_image:
            width, height = self.background_image.size
            self.root.geometry(f"{width}x{height}")

    def load_video(self):
        file_path = self.file_loader.load_video(initialdir=self.last_opened_files.get("video_folder", os.getcwd()))
        if not file_path:
            return
        self.last_opened_files["video"] = file_path
        self.last_opened_files["video_folder"] = os.path.dirname(file_path)
        self.save_last_opened_files()
        self.current_video_path = file_path
        self.video_label_widget.config(text="Video loaded, ready to play")

    def play_video_controls(self):
        if not self.current_video_path:
            self.video_label_widget.config(text="No video loaded.")
            return
        self.pause_video_flag = False
        self.play_video(self.current_video_path)

    def pause_video_controls(self):
        self.pause_video_flag = True

    def stop_video_controls(self):
        self.stop_video_flag = True
        if self.video_thread and self.video_thread.is_alive():
            self.root.after(100, self.check_video_thread)
        self.video_label_widget.config(image="", text="No video loaded")

    def check_video_thread(self):
        if self.video_thread and self.video_thread.is_alive():
            self.root.after(100, self.check_video_thread)  # Keep checking every 100ms
        else:
            self.video_thread = None  # Reset the thread once it has stopped

    def play_video(self, file_path):
        if self.video_thread and self.video_thread.is_alive():
            self.stop_video_flag = True
            self.video_thread.join()

        self.stop_video_flag = False

        def video_loop():
            cap = cv2.VideoCapture(file_path)
            while cap.isOpened() and not self.stop_video_flag:
                if self.pause_video_flag:
                    continue

                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (self.video_frame.winfo_width(), self.video_frame.winfo_height()))
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.video_label_widget.config(image=photo, text="")
                self.video_label_widget.image = photo
                self.root.update()

            cap.release()

        self.video_thread = Thread(target=video_loop)
        self.video_thread.start()

    def load_shotcut(self):
        file_path = self.file_loader.load_shortcut(initialdir=self.last_opened_files.get("shortcut_folder", os.getcwd()))
        if not file_path:
            return
        self.last_opened_files["shortcut"] = file_path
        self.last_opened_files["shortcut_folder"] = os.path.dirname(file_path)
        self.save_last_opened_files()
        self.file_label.config(text=f"File: {os.path.basename(file_path)}")
        self.markers = self.media_handler.extract_markers_from_file(file_path) or []
        self.display_markers()

    def auto_load_markers(self):
        shortcut_file = self.last_opened_files.get("shortcut")
        if shortcut_file and os.path.exists(shortcut_file):
            self.file_label.config(text=f"File: {os.path.basename(shortcut_file)}")
            self.markers = self.media_handler.extract_markers_from_file(shortcut_file) or []
            self.display_markers()

    def display_markers(self):
        for item in self.marker_tree.get_children():
            self.marker_tree.delete(item)
        for marker in self.markers:
            self.marker_tree.insert("", "end", values=(marker["Number"], marker["Name"], marker["Time"], marker.get("Picture", ""), marker.get("Video", "")))

    def open_settings(self):
        def save_background_image(selected_image):
            self.last_opened_files["background_image"] = selected_image
            self.save_last_opened_files()
            if selected_image:
                self.set_background_image(selected_image)

        from gui.settings_window import SettingsWindow
        SettingsWindow(self.root, self.background_image_path, save_background_image)

    def load_last_opened_files(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                return json.load(file)
        return {"image": None, "image_folder": None, "video": None, "video_folder": None, "shortcut": None, "shortcut_folder": None}

    def save_last_opened_files(self):
        with open(self.config_file, "w") as file:
            json.dump(self.last_opened_files, file, indent=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
