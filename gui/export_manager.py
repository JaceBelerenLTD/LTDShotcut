import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk  # Import tkinter for `tk.END`
from tkinter import messagebox
import os
import json
import difflib
import xml.etree.ElementTree as ET
import hashlib
from datetime import datetime
from xml.dom import minidom

class ExportManager:
    def __init__(self, parent, markers):
        self.parent = parent
        self.markers = markers

        # Create the Export Manager window
        self.window = ttk.Toplevel(parent)
        self.window.title("Export Manager")
        self.window.geometry("2000x1200")
        self.config = self.load_config()
        self.debug_markers()

        # Set up the UI layout
        self.setup_ui()

    def debug_markers(self):
        """Display debug information about the markers."""
        if not self.markers:
            print("Debug: No markers loaded.")
        else:
            print(f"Debug: {len(self.markers)} markers loaded.")
            for index, marker in enumerate(self.markers):
                print(f"Marker {index + 1}: {marker}")

    def highlight_differences(self):
        """Highlight differences between the original .mlt file and the output preview."""
        mlt_file = self.config.get("shortcut", None)
        if not mlt_file or not os.path.exists(mlt_file):
            messagebox.showerror("Error", "No valid .mlt file found in config.")
            return

        try:
            # Read the original content
            with open(mlt_file, "r", encoding="utf-8") as file:
                original_content = [line.strip() for line in file.readlines()]  # Strip whitespace

            # Get the output preview content
            output_content = [
                line.strip() for line in self.output_mlt_text.get("1.0", "end").splitlines()
            ]  # Strip whitespace

            # Clear existing tags in both text widgets
            self.current_mlt_text.tag_delete("diff")
            self.output_mlt_text.tag_delete("diff")

            # Compare the files line by line using difflib
            matcher = difflib.SequenceMatcher(None, original_content, output_content)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == "replace":  # Lines that differ
                    for i in range(i1, i2):
                        self.current_mlt_text.tag_add("diff", f"{i + 1}.0", f"{i + 1}.end")
                    for j in range(j1, j2):
                        self.output_mlt_text.tag_add("diff", f"{j + 1}.0", f"{j + 1}.end")
                elif tag == "delete":  # Lines deleted from the original
                    for i in range(i1, i2):
                        self.current_mlt_text.tag_add("diff", f"{i + 1}.0", f"{i + 1}.end")
                elif tag == "insert":  # Lines added to the output
                    for j in range(j1, j2):
                        self.output_mlt_text.tag_add("diff", f"{j + 1}.0", f"{j + 1}.end")

            # Configure the highlight tag
            self.current_mlt_text.tag_configure("diff", background="lightcoral")
            self.output_mlt_text.tag_configure("diff", background="lightgreen")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to highlight differences:\n{e}")

    

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
        """Set up the Export Manager UI using ttkbootstrap."""
        # Frames for current and output .mlt file display
        left_frame = ttk.Frame(self.window, padding=10, bootstyle="info")
        right_frame = ttk.Frame(self.window, padding=10, bootstyle="success")

        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Add headers for each panel
        ttk.Label(left_frame, text="Current .mlt File", font=("Helvetica", 14, "bold")).pack(pady=5)
        ttk.Label(right_frame, text="Output Preview", font=("Helvetica", 14, "bold")).pack(pady=5)

        # Text widgets to display .mlt content
        self.current_mlt_text = ttk.ScrolledText(left_frame, height=30, width=100)
        self.current_mlt_text.pack(fill="both", expand=True, padx=10, pady=10)

        self.output_mlt_text = ttk.ScrolledText(right_frame, height=30, width=100)
        self.output_mlt_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Load initial content
        self.load_current_mlt()

        # Add buttons under the text boxes
        self.add_buttons(left_frame, right_frame)

    def add_transitions(self):
        """Add '1' to the end of the existing content in the output text box or the original .mlt file."""
        # Check if there's content in the output text box
        existing_output_content = self.output_mlt_text.get("1.0", tk.END).strip()

        # If output text box has content, append '1' to it
        if existing_output_content:
            updated_content = existing_output_content.rstrip() + "\nadd_transitions"
        else:
            # Otherwise, load content from the .mlt file
            mlt_file = self.config.get("shortcut", None)
            if not mlt_file or not os.path.exists(mlt_file):
                messagebox.showerror("Error", "No valid .mlt file found in config.")
                return

            try:
                # Open the file and read its content
                with open(mlt_file, "r", encoding="utf-8") as file:
                    content = file.read()

                # Append '1' to the file content
                updated_content = content.rstrip() + "\nadd_transitions"

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while adding transitions:\n{e}")
                return

        # Display the updated content in the Output Preview
        self.load_output_preview(updated_content)

    def add_producer(self):
        """Add producers for each marker in the .mlt file."""
        # Load the .mlt file path from the configuration
        mlt_file = self.config.get("shortcut", None)
        if not mlt_file or not os.path.exists(mlt_file):
            print("Error: No valid .mlt file found in config.")
            return

        # Read the .mlt file
        with open(mlt_file, "r", encoding="utf-8") as file:
            content = file.read()

        # Parse the .mlt file as XML
        root = ET.fromstring(content)

        # Find the current highest producer number
        highest_producer_id = 0
        for producer in root.findall(".//producer"):
            producer_id = producer.get("id", "")
            if producer_id.startswith("producer"):
                try:
                    producer_number = int(producer_id.replace("producer", ""))
                    highest_producer_id = max(highest_producer_id, producer_number)
                except ValueError:
                    pass

        # Add a producer for each marker
        for marker in self.markers:
            # Extract the full picture path from the marker
            picture_path = marker.get("Picture", "").strip()
            if not picture_path:
                print(f"Warning: Marker {marker.get('Number')} ('{marker.get('Name', 'Unnamed')}') does not have an associated picture path.")
                continue

            if not os.path.exists(picture_path):
                print(f"Error: Picture path for Marker {marker.get('Number')} ('{marker.get('Name', 'Unnamed')}') does not exist: {picture_path}")
                continue

            highest_producer_id += 1  # Increment the producer ID
            producer_id = f"producer{highest_producer_id}"

            # Calculate the unique hash for this producer
            marker_name = marker.get("Name", "unknown")
            hash_input = f"{marker_name}_{datetime.utcnow().isoformat()}".encode("utf-8")
            unique_hash = hashlib.md5(hash_input).hexdigest()  # Generate a 32-character hash

            # Get the current datetime in the required format
            creation_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

            # Create the producer element
            producer = ET.Element("producer", id=producer_id)
            ET.SubElement(producer, "property", name="length").text = "04:00:00.000"
            ET.SubElement(producer, "property", name="eof").text = "pause"
            ET.SubElement(producer, "property", name="resource").text = picture_path  # Use the full path
            ET.SubElement(producer, "property", name="ttl").text = "1"
            ET.SubElement(producer, "property", name="aspect_ratio").text = "1"
            ET.SubElement(producer, "property", name="meta.media.progressive").text = "1"
            ET.SubElement(producer, "property", name="seekable").text = "1"
            ET.SubElement(producer, "property", name="format").text = "2"
            ET.SubElement(producer, "property", name="meta.media.width").text = "1920"
            ET.SubElement(producer, "property", name="meta.media.height").text = "1080"
            ET.SubElement(producer, "property", name="mlt_service").text = "qimage"
            ET.SubElement(producer, "property", name="creation_time").text = creation_time
            ET.SubElement(producer, "property", name="shotcut:hash").text = unique_hash
            ET.SubElement(producer, "property", name="shotcut:caption").text = os.path.basename(picture_path)

            # Insert the producer element before the closing </mlt> tag
            playlist = root.find(".//playlist[last()]")
            if playlist is not None:
                root.insert(list(root).index(playlist) + 1, producer)

        # Serialize the updated XML back to a string
        pretty_string = prettify_xml_with_no_extra_lines(root)

        # Load the updated content into the Output Preview
        self.load_output_preview(pretty_string)



    def prettify_xml_with_no_extra_lines(element):
        """Prettify XML while removing extra blank lines."""
        rough_string = ET.tostring(element, encoding="unicode", method="xml")
        parsed = minidom.parseString(rough_string)
        return "\n".join([line for line in parsed.toprettyxml(indent="  ").splitlines() if line.strip()])
    
    def add_buttons(self, left_frame, right_frame):
        """Add buttons under the textboxes."""
        # Button frame for the left side
        left_button_frame = ttk.Frame(left_frame)
        left_button_frame.pack(fill="x", pady=10)

        # Add buttons for the left side
        ttk.Button(left_button_frame, text="Add Transitions", bootstyle="primary", command=self.add_transitions).pack(side="left", expand=True, padx=5)
        ttk.Button(left_button_frame, text="Add Producer", bootstyle="secondary", command=self.add_producer).pack(side="left", expand=True, padx=5)
        ttk.Button(left_button_frame, text="Highlight Differences", bootstyle="info", command=self.highlight_differences).pack(side="left", expand=True, padx=5)

        # Button frame for the right side
        right_button_frame = ttk.Frame(right_frame)
        right_button_frame.pack(fill="x", pady=10)

        # Add buttons for the right side
        ttk.Button(right_button_frame, text="Button 4", bootstyle="warning", command=lambda: self.show_message("I'm here from Button 4")).pack(side="left", expand=True, padx=5)
        ttk.Button(right_button_frame, text="Button 5", bootstyle="danger", command=lambda: self.show_message("I'm here from Button 5")).pack(side="left", expand=True, padx=5)
        ttk.Button(right_button_frame, text="Export", bootstyle="success", command=self.export_output).pack(side="left", expand=True, padx=5)

    def show_message(self, message):
        """Display a simple message box."""
        messagebox.showinfo(title="Message", message=message)

    def load_current_mlt(self):
        """Load the content of the current .mlt file into the left panel."""
        mlt_file = self.config.get("shortcut", None)
        if not mlt_file or not os.path.exists(mlt_file):
            self.current_mlt_text.insert("1.0", "Error: No valid .mlt file found in config.")
            return

        with open(mlt_file, "r", encoding="utf-8") as file:
            content = file.read()

        self.current_mlt_text.delete("1.0", ttk.END)
        self.current_mlt_text.insert("1.0", content)

    def load_output_preview(self, output_content):
        """Load simulated output content into the right panel."""
        self.output_mlt_text.delete("1.0", ttk.END)
        self.output_mlt_text.insert("1.0", output_content)

    def export_output(self):
        """Export the output preview content to the export folder."""
        export_folder = self.config.get("export_folder", None)
        if not export_folder or not os.path.exists(export_folder):
            messagebox.showerror("Export Error", "Export folder is not set or does not exist.")
            return

        # Get the content of the output preview
        output_content = self.output_mlt_text.get("1.0", ttk.END).strip()
        if not output_content:
            messagebox.showerror("Export Error", "Output content is empty.")
            return

        # Define the export file path
        export_file_path = os.path.join(export_folder, "exported_file.mlt")
        try:
            with open(export_file_path, "w", encoding="utf-8") as file:
                file.write(output_content)
            messagebox.showinfo("Export Successful", f"File successfully exported to:\n{export_file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export the file:\n{e}")
            
def prettify_xml_with_no_extra_lines(element):
        """Prettify XML and remove unnecessary blank lines."""
        rough_string = ET.tostring(element, encoding="utf-8")
        pretty_string = minidom.parseString(rough_string).toprettyxml(indent="  ")
        # Remove extra blank lines
        lines = [line for line in pretty_string.splitlines() if line.strip()]
        return "\n".join(lines)

if __name__ == "__main__":
    # For testing purposes only
    app = ttk.Window(themename="flatly")
    ExportManager(app)
    app.mainloop()
