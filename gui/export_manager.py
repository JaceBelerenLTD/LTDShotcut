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
        
    def add_playlists(self):
        """
        Add a playlist for the markers to the .mlt file, ensuring the playlist is added 
        immediately after the producers.
        """
        # Check if there's content in the output text box
        existing_output_content = self.output_mlt_text.get("1.0", tk.END).strip()

        # Use existing content from the output text box if available; otherwise, use the .mlt file
        if existing_output_content:
            content = existing_output_content
        else:
            mlt_file = self.config.get("shortcut", None)
            if not mlt_file or not os.path.exists(mlt_file):
                print("Error: No valid .mlt file found in config.")
                return
            with open(mlt_file, "r", encoding="utf-8") as file:
                content = file.read()

        # Parse the .mlt file as XML
        root = ET.fromstring(content)

        # Find the current highest playlist ID
        highest_playlist_id = 0
        for playlist in root.findall(".//playlist"):
            playlist_id = playlist.get("id", "")
            if playlist_id.startswith("playlist"):
                try:
                    playlist_number = int(playlist_id.replace("playlist", ""))
                    highest_playlist_id = max(highest_playlist_id, playlist_number)
                except ValueError:
                    pass

        # Increment for the new playlist ID
        new_playlist_id = highest_playlist_id + 1
        playlist_id = f"playlist{new_playlist_id}"

        # Create the playlist element
        playlist = ET.Element("playlist", id=playlist_id)
        ET.SubElement(playlist, "property", name="shotcut:video").text = "1"
        ET.SubElement(playlist, "property", name="shotcut:name").text = f"V{new_playlist_id}"

        # Track the previous marker time
        previous_time = None

        for idx, marker in enumerate(self.markers):
            # Adjust producer ID based on index to start from producer0
            producer_id = f"producer{idx}"  # Sequentially number producers starting from 0

            # Verify if the corresponding producer exists in the XML
            if not any(producer.get("id") == f"producer{idx}" for producer in root.findall(".//producer")):
                # Skip markers without a valid producer in the XML
                print(f"Skipping marker '{marker['Name']}' as it has no valid producer.")
                continue
            # If it's the first marker, calculate blank from start time to 0:00:00
            if idx == 1 and marker["StartTime"]:
                blank_length = self.calculate_time_difference("00:00:00.000", marker["StartTime"])
                ET.SubElement(playlist, "blank", length=blank_length)
            # Add a blank element if there was a previous marker
            if previous_time:
                blank_length = self.calculate_time_difference(previous_time, marker["StartTime"])
                ET.SubElement(playlist, "blank", length=blank_length)

            # Add the entry for this marker
           # adjusted_producer_id = f"producer{int(producer_id.replace('producer', '')) - 1}"
            ET.SubElement(playlist, "entry", producer=producer_id, **{"in": "00:00:00.000", "out": "00:00:00.483"})

            previous_time = marker["StartTime"]
            
        # Add the playlist to the XML
        last_playlist = root.find(".//playlist[last()]")
        if last_playlist is not None:
            root.insert(list(root).index(last_playlist) + 1, playlist)

        # Add the corresponding track in the <tractor> element
            tractor = root.find(".//tractor")
            if tractor is not None:
                # Insert the new track for the playlist after the last existing track
                new_track = ET.Element("track", producer=playlist_id)
                tracks = tractor.findall(".//track")
                if tracks:
                    tractor.insert(list(tractor).index(tracks[-1]) + 1, new_track)
                else:
                    # If no tracks are found, add it as the first child of <tractor>
                    tractor.insert(0, new_track)

        # Serialize the updated XML back to a string
        pretty_string = prettify_xml_with_no_extra_lines(root)

        # Load the updated content into the Output Preview
        self.load_output_preview(pretty_string)



    def calculate_time_difference(self, start_time, end_time):
        """
        Calculate the difference between two times in the format HH:MM:SS.mmm.
        Returns the difference as a formatted string.
        """
        from datetime import datetime

        time_format = "%H:%M:%S.%f"
        start = datetime.strptime(start_time, time_format)
        end = datetime.strptime(end_time, time_format)
        difference = end - start
        total_seconds = int(difference.total_seconds())
        milliseconds = int((difference.total_seconds() - total_seconds) * 1000)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"



    def calculate_adjusted_duration(self, start, end, out_duration):
        """
        Calculate the duration between two timecodes in HH:MM:SS.MMM format,
        adjusted for the out_duration.

        Args:
            start (str): Start time in "HH:MM:SS.MMM" format.
            end (str): End time in "HH:MM:SS.MMM" format.
            out_duration (str): The fixed out duration to subtract.

        Returns:
            str: Duration in "HH:MM:SS.MMM" format.
        """
        from datetime import datetime, timedelta

        fmt = "%H:%M:%S.%f"
        start_dt = datetime.strptime(start, fmt)
        end_dt = datetime.strptime(end, fmt)
        out_dt = datetime.strptime(out_duration, fmt) - datetime.strptime("00:00:00.000", fmt)

        # Calculate the difference and subtract the out duration
        delta = end_dt - start_dt - timedelta(seconds=out_dt.total_seconds())
        delta_seconds = delta.total_seconds()

        # Convert seconds back to HH:MM:SS.MMM format
        hours = int(delta_seconds // 3600)
        minutes = int((delta_seconds % 3600) // 60)
        seconds = int(delta_seconds % 60)
        milliseconds = int((delta_seconds % 1) * 1000)

        return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"




    def add_producer(self):
        """
        Add producers to the .mlt file based on markers.
        If a marker does not have a picture, it will be skipped with a warning.
        """
        # Check if the output preview has content; use it as the base if present
        existing_output_content = self.output_mlt_text.get("1.0", tk.END).strip()

        if existing_output_content:
            content = existing_output_content
        else:
            # Otherwise, load content from the .mlt file
            mlt_file = self.config.get("shortcut", None)
            if not mlt_file or not os.path.exists(mlt_file):
                print("Error: No valid .mlt file found in config.")
                return

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
            marker_name = marker.get("Name", "unknown")
            marker_picture = marker.get("Picture", None)

            # Skip markers without pictures
            if not marker_picture:
                print(f"Warning: Marker '{marker_name}' has no picture assigned. Skipping.")
                continue

            highest_producer_id += 1  # Increment the producer ID
            producer_id = f"producer{highest_producer_id}"

            # Generate a unique hash
            hash_input = f"{marker_name}_{datetime.utcnow().isoformat()}".encode("utf-8")
            unique_hash = hashlib.md5(hash_input).hexdigest()

            # Get the current datetime in the required format
            creation_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

            # Create the producer element
            producer = ET.Element("producer", id=producer_id, attrib={"in": "00:00:00.000", "out": "03:59:59.983"})
            ET.SubElement(producer, "property", name="length").text = "04:00:00.000"
            ET.SubElement(producer, "property", name="eof").text = "pause"
            ET.SubElement(producer, "property", name="resource").text = marker_picture.replace("\\", "/")  # Ensure correct slashes
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
            ET.SubElement(producer, "property", name="shotcut:caption").text = os.path.basename(marker_picture)

            # Add the producer element before the last </mlt> or </playlist>
            playlist = root.find(".//playlist[last()]")
            if playlist is not None:
                root.insert(list(root).index(playlist) + 1, producer)

        # Serialize the updated XML back to a string
        pretty_string = prettify_xml_with_no_extra_lines(root)

        # Load the updated content into the Output Preview
        self.load_output_preview(pretty_string)
 

    def add_transitions(self):
        """
        Adds necessary transitions before the `</tractor>` tag, ensuring proper sequencing
        and adding only missing transitions starting from the lowest available ID.
        """
        # Determine the base content (from output preview or original file)
        existing_output_content = self.output_mlt_text.get("1.0", tk.END).strip()
        if existing_output_content:
            content = existing_output_content
        else:
            mlt_file = self.config.get("shortcut", None)
            if not mlt_file or not os.path.exists(mlt_file):
                print("Error: No valid .mlt file found in config.")
                return
            with open(mlt_file, "r", encoding="utf-8") as file:
                content = file.read()

        # Parse the XML content
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return

        # Locate the tractor element
        tractor = root.find(".//tractor")
        if tractor is None:
            print("No <tractor> element found in the XML.")
            return

        # Extract existing transition IDs
        existing_transition_ids = {
            int(trans.get("id").replace("transition", ""))
            for trans in tractor.findall("transition")
            if trans.get("id", "").startswith("transition") and trans.get("id").replace("transition", "").isdigit()
        }

        # Find the lowest available transition ID
        next_transition_id = 1
        while next_transition_id in existing_transition_ids:
            next_transition_id += 1

        # Define the necessary transitions
        required_transitions = [
            {"a_track": "0", "b_track": "4", "mlt_service": "mix", "always_active": "1", "sum": "1"},
            {"a_track": "1", "b_track": "4", "mlt_service": "frei0r.cairoblend", "version": "0.1", "threads": "0", "disable": "0"},
        ]

        # Generate missing transitions
        for transition in required_transitions:
            # Check if a similar transition exists
            transition_exists = any(
                all(
                    prop.get("name") == key and prop.text == value
                    for prop in trans.findall("property")
                    for key, value in transition.items()
                    if key not in {"a_track", "b_track"}
                )
                for trans in tractor.findall("transition")
                if trans.find("property[@name='a_track']") is not None and
                trans.find("property[@name='b_track']") is not None and
                trans.find("property[@name='a_track']").text == transition["a_track"] and
                trans.find("property[@name='b_track']").text == transition["b_track"]
            )
            if not transition_exists:
                # Add the new transition with the next available ID
                new_transition_id = f"transition{next_transition_id}"
                new_transition = ET.SubElement(tractor, "transition", id=new_transition_id)
                for key, value in transition.items():
                    ET.SubElement(new_transition, "property", name=key).text = value
                next_transition_id += 1  # Increment the transition ID for the next one

        # Serialize back to string and load into the output preview
        pretty_string = prettify_xml_with_no_extra_lines(root)
        self.load_output_preview(pretty_string)
        print(f"Transitions added successfully.")




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
        ttk.Button(left_button_frame, text="Add Producer", bootstyle="secondary", command=self.add_producer).pack(side="left", expand=True, padx=5)
        ttk.Button(left_button_frame, text="Add Playlists", bootstyle="primary", command=self.add_playlists).pack(side="left", expand=True, padx=5)
        ttk.Button(left_button_frame, text="Add Transitions", bootstyle="warning", command=self.add_transitions).pack(side="left", expand=True, padx=5)

        # Button frame for the right side
        right_button_frame = ttk.Frame(right_frame)
        right_button_frame.pack(fill="x", pady=10)

        # Add buttons for the right side
        ttk.Button(right_button_frame, text="Highlight Differences", bootstyle="info", command=self.highlight_differences).pack(side="left", expand=True, padx=5)
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
