import json
import os
import cv2
from PIL import Image, ImageTk  # For displaying images
from tkinter import ttk
import tkinter as tk
from Services.file_loader import FileLoader
from Services.media_handler import MediaHandler
from threading import Thread  # To handle video playback without freezing the GUI


class MainWindow:
    def __init__(self, root):
        """
        MainWindow constructor that sets up the main application layout.
        """
        self.root = root
        self.root.title("Media Display App")

        # Initialize file and media handlers
        self.file_loader = FileLoader()
        self.media_handler = MediaHandler()

        # Variables for image and video handling
        self.image_label_widget = None
        self.video_label_widget = None
        self.video_thread = None
        self.stop_video_flag = False
        self.pause_video_flag = False

        # Last loaded markers
        self.markers = []

        # Load persistent data
        self.config_file = "config.json"
        self.last_opened_files = self.load_last_opened_files()

        # Create frames for widgets
        self.image_frame = ttk.Frame(self.root, style="Debug.TFrame")
        self.video_frame = ttk.Frame(self.root, style="Debug.TFrame")
        self.text_frame = ttk.Frame(self.root, style="Debug.TFrame")  # Frame for file name and markers grid
        self.controls_frame = ttk.Frame(self.root, style="Debug.TFrame")

        # Debugging style for frames
        style = ttk.Style()
        style.configure("Debug.TFrame", background="lightblue", borderwidth=1, relief="solid")

        # Place the frames using grid
        self.image_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.video_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.text_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.controls_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Image and video labels
        self.image_label_widget = ttk.Label(self.image_frame, text="1: No image loaded", anchor="center")
        self.image_label_widget.pack(fill="both", expand=True)

        self.video_label_widget = ttk.Label(self.video_frame, text="2: No video loaded", anchor="center")
        self.video_label_widget.pack(fill="both", expand=True)

        # Text frame setup
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

        ttk.Label(self.controls_frame, text="4", font=("Arial", 20), foreground="purple").pack(pady=10)

        # Add action buttons to the controls_frame
        self.load_image_button = ttk.Button(self.controls_frame, text="Load Image", command=self.load_image)
        self.load_video_button = ttk.Button(self.controls_frame, text="Load Video", command=self.load_video)
        self.load_shotcut_button = ttk.Button(self.controls_frame, text="Load Shotcut File", command=self.load_shotcut)
        self.settings_button = ttk.Button(self.controls_frame, text="Settings", command=self.open_settings)

        self.play_button = ttk.Button(self.controls_frame, text="Play", command=self.play_video_controls)
        self.pause_button = ttk.Button(self.controls_frame, text="Pause", command=self.pause_video_controls)

        self.load_image_button.pack(pady=5)
        self.load_video_button.pack(pady=5)
        self.load_shotcut_button.pack(pady=5)
        self.play_button.pack(pady=5)
        self.pause_button.pack(pady=5)
        self.settings_button.pack(pady=5)

        # Auto-load markers from the last opened shortcut file
        self.auto_load_markers()

    def load_image(self):
        file_path = self.file_loader.load_image(initialdir=self.last_opened_files.get("image_folder", os.getcwd()))
        if file_path:
            self.last_opened_files["image"] = file_path
            self.last_opened_files["image_folder"] = os.path.dirname(file_path)
            self.save_last_opened_files()
            self.update_labels()
            self.display_image(file_path)

    def display_image(self, file_path):
        image = Image.open(file_path)
        image = image.resize((self.image_frame.winfo_width(), self.image_frame.winfo_height()), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        self.image_label_widget.config(image=photo, text="")
        self.image_label_widget.image = photo

    def load_video(self):
        file_path = self.file_loader.load_video(initialdir=self.last_opened_files.get("video_folder", os.getcwd()))
        if file_path:
            self.last_opened_files["video"] = file_path
            self.last_opened_files["video_folder"] = os.path.dirname(file_path)
            self.save_last_opened_files()
            self.update_labels()

    def play_video_controls(self):
        if self.last_opened_files.get("video"):
            self.pause_video_flag = False
            self.play_video(self.last_opened_files["video"])

    def pause_video_controls(self):
        self.pause_video_flag = True

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
        if file_path and (file_path.endswith(".mlt") or file_path.endswith(".xml")):
            self.last_opened_files["shortcut"] = file_path
            self.last_opened_files["shortcut_folder"] = os.path.dirname(file_path)
            self.save_last_opened_files()
            self.update_labels()
            self.file_label.config(text=f"File: {os.path.basename(file_path)}")
            self.markers = self.media_handler.extract_markers_from_file(file_path)
            self.display_markers()

    def auto_load_markers(self):
        shortcut_file = self.last_opened_files.get("shortcut")
        if shortcut_file and os.path.exists(shortcut_file) and (shortcut_file.endswith(".mlt") or shortcut_file.endswith(".xml")):
            self.file_label.config(text=f"File: {os.path.basename(shortcut_file)}")
            self.markers = self.media_handler.extract_markers_from_file(shortcut_file)
            self.display_markers()

    def display_markers(self):
        for item in self.marker_tree.get_children():
            self.marker_tree.delete(item)
        for marker in self.markers:
            self.marker_tree.insert("", "end", values=(marker["Number"], marker["Name"], marker["Time"], marker.get("Picture", ""), marker.get("Video", "")))

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        tk.Label(settings_window, text="Last Opened Files", font=("Arial", 14)).pack(pady=10)
        for key, file_path in self.last_opened_files.items():
            tk.Label(settings_window, text=f"{key.capitalize()}: {file_path or 'None'}", anchor="w").pack(fill="x", padx=20, pady=5)
        tk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=20)

    def update_labels(self):
        self.image_label_widget.config(text=f"1: {os.path.basename(self.last_opened_files['image']) if self.last_opened_files['image'] else 'No image loaded'}")
        self.video_label_widget.config(text=f"2: {os.path.basename(self.last_opened_files['video']) if self.last_opened_files['video'] else 'No video loaded'}")
        self.file_label.config(text=f"File: {os.path.basename(self.last_opened_files['shortcut']) if self.last_opened_files['shortcut'] else 'No file loaded'}")

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
