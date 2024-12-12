import tkinter as tk
from tkinter import ttk
import os
import json
from resources.styles import BACKGROUND_COLOR
from tkinter import messagebox
import xml.etree.ElementTree as ET


class ExportManager:
    def __init__(self, parent):
        self.parent = parent

        # Create the Export Manager window
        self.window = tk.Toplevel(parent)
        self.window.title("Export Manager")
        self.window.geometry("2000x1200")
        self.window.configure(bg=BACKGROUND_COLOR)

        # Load config
        self.config = self.load_config()

        # Set up the UI layout
        self.setup_ui()

    def load_config(self):
        """Load configuration from config.json."""
        config_file = "config.json"
        if os.path.exists(config_file):
            with open(config_file, "r") as file:
                try:
                    config = json.load(file)
                    print(f"Debug: Loaded config: {config}")
                    return config
                except json.JSONDecodeError:
                    print("Error: Failed to decode config.json.")
        return {}

    def setup_ui(self):
        """Set up the Export Manager UI."""
        # Frames for current and output .mlt file display
        left_frame = ttk.Frame(self.window, padding=10)
        right_frame = ttk.Frame(self.window, padding=10)

        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Add headers for each panel
        ttk.Label(left_frame, text="Current .mlt File", font=("Arial", 14, "bold")).pack(pady=5)
        ttk.Label(right_frame, text="Output Preview", font=("Arial", 14, "bold")).pack(pady=5)

        # Text widgets to display .mlt content
        self.current_mlt_text = tk.Text(left_frame, wrap="word", state="normal", bg="lightgrey")
        self.current_mlt_text.pack(fill="both", expand=True, padx=10, pady=10)

        self.output_mlt_text = tk.Text(right_frame, wrap="word", state="normal", bg="lightgrey")
        self.output_mlt_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Load initial content
        self.load_current_mlt()

        # Add buttons under the text boxes
        self.add_buttons(left_frame, right_frame)

    def add_buttons(self, left_frame, right_frame):
        """Add buttons under the textboxes."""
        # Button frame for the left side
        left_button_frame = ttk.Frame(left_frame)
        left_button_frame.pack(fill="x", pady=10)

        # Add buttons for the left side
        ttk.Button(left_button_frame, text="Button 1", command=lambda: self.show_message("I'm here from Button 1")).pack(side="left", expand=True, padx=5)
        ttk.Button(left_button_frame, text="Add Transitions & Track", command=self.add_transitions_and_track).pack(side="left", expand=True, padx=5)
        ttk.Button(left_button_frame, text="Button 3", command=lambda: self.show_message("I'm here from Button 3")).pack(side="left", expand=True, padx=5)

        # Button frame for the right side
        right_button_frame = ttk.Frame(right_frame)
        right_button_frame.pack(fill="x", pady=10)

        # Add buttons for the right side
        ttk.Button(right_button_frame, text="Button 4", command=lambda: self.show_message("I'm here from Button 4")).pack(side="left", expand=True, padx=5)
        ttk.Button(right_button_frame, text="Button 5", command=lambda: self.show_message("I'm here from Button 5")).pack(side="left", expand=True, padx=5)
        ttk.Button(right_button_frame, text="Export", command=self.export_output).pack(side="left", expand=True, padx=5)

    def show_message(self, message):
        """Display a simple message box."""
        new_window = tk.Toplevel(self.window)
        new_window.title("Message")
        new_window.geometry("200x100")
        ttk.Label(new_window, text=message, font=("Arial", 12)).pack(expand=True, padx=10, pady=10)

    def load_current_mlt(self):
        """Load the content of the current .mlt file into the left panel."""
        mlt_file = self.config.get("shortcut", None)
        if not mlt_file or not os.path.exists(mlt_file):
            self.current_mlt_text.insert("1.0", "Error: No valid .mlt file found in config.")
            return

        with open(mlt_file, "r") as file:
            content = file.read()

        self.current_mlt_text.delete("1.0", tk.END)
        self.current_mlt_text.insert("1.0", content)

    def load_output_preview(self, output_content):
        """Load simulated output content into the right panel."""
        self.output_mlt_text.delete("1.0", tk.END)
        self.output_mlt_text.insert("1.0", output_content)

    def add_transitions_and_track(self):
        """Add transitions and a track to the current .mlt file and update the output preview."""
        mlt_file = self.config.get("shortcut", None)
        if not mlt_file or not os.path.exists(mlt_file):
            messagebox.showerror("Error", "No valid .mlt file found in config.")
            return

        try:
            # Parse the input MLT XML file
            tree = ET.parse(mlt_file)
            root = tree.getroot()

            # Add Transitions
            transitions = [
                {
                    "id": "transition2",
                    "a_track": "0",
                    "b_track": "1",
                    "mlt_service": "affine",
                    "in": "00:00:05.000",
                    "out": "00:00:10.000"
                },
                {
                    "id": "transition3",
                    "a_track": "1",
                    "b_track": "2",
                    "mlt_service": "luma",
                    "in": "00:00:10.000",
                    "out": "00:00:15.000"
                }
            ]

            for transition in transitions:
                transition_elem = ET.Element("transition", attrib={"id": transition["id"]})
                for key, value in transition.items():
                    if key != "id":
                        ET.SubElement(transition_elem, "property", name=key).text = value
                root.append(transition_elem)

            # Add Track
            playlist_elem = root.find("./playlist[@id='playlist0']")
            if playlist_elem is not None:
                track_elem = ET.Element("track", attrib={"producer": "playlist3"})
                playlist_elem.append(track_elem)

            # Convert updated XML to a string
            output_content = ET.tostring(root, encoding="unicode")

            # Load the updated content into the right panel
            self.load_output_preview(output_content)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while adding transitions and track:\n{e}")

    def export_output(self): 
        """Export the output preview content to the export folder."""
        export_folder = self.config.get("export_folder", None)
        if not export_folder or not os.path.exists(export_folder):
            messagebox.showerror("Export Error", "Export folder is not set or does not exist.")
            return

        # Get the content of the output preview
        output_content = self.output_mlt_text.get("1.0", tk.END).strip()
        if not output_content:
            messagebox.showerror("Export Error", "Output content is empty.")
            return

        # Define the export file path
        export_file_path = os.path.join(export_folder, "exported_file.mlt")
        try:
            with open(export_file_path, "w") as file:
                file.write(output_content)
            messagebox.showinfo("Export Successful", f"File successfully exported to:\n{export_file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export the file:\n{e}")


if __name__ == "__main__":
    # For testing purposes only
    root = tk.Tk()
    root.withdraw()
    ExportManager(root)
    root.mainloop()
