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
        Adds a playlist element to the output file based on the markers and producers.
        """
        # Check if there's content in the output text box
        existing_output_content = self.output_mlt_text.get("1.0", tk.END).strip()

        if existing_output_content:
            # Use the existing content in the output preview as the base
            content = existing_output_content
        else:
            # Otherwise, load content from the .mlt file
            mlt_file = self.config.get("shortcut", None)
            if not mlt_file or not os.path.exists(mlt_file):
                print("Error: No valid .mlt file found in config.")
                return

            with open(mlt_file, "r", encoding="utf-8") as file:
                content = file.read()

        # Parse the content as XML
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

        # Determine the new playlist ID
        new_playlist_id = f"playlist{highest_playlist_id + 1}"

        # Create the playlist element
        playlist = ET.Element("playlist", id=new_playlist_id)
        ET.SubElement(playlist, "property", name="shotcut:video").text = "1"
        ET.SubElement(playlist, "property", name="shotcut:name").text = f"V{highest_playlist_id + 1}"

        # Sort markers by their start time
        sorted_markers = sorted(self.markers, key=lambda x: x.get("StartTime", "00:00:00.000"))

        # Add blanks and entries based on markers
        previous_time = "00:00:00.000"  # Start at the beginning of the timeline
        out_duration = "00:00:00.483"  # Fixed out duration for each entry
        for marker in sorted_markers:
            marker_start_time = marker.get("StartTime", "00:00:00.000")
            producer_id = f"producer{marker['Number']}"  # Assuming marker['Number'] corresponds to producer numbers

            # Calculate the blank length
            blank_length = self.calculate_adjusted_duration(previous_time, marker_start_time, out_duration)

            # Add a blank for the marker start time
            ET.SubElement(playlist, "blank", length=blank_length)

            # Add an entry for the producer
            ET.SubElement(playlist, "entry", producer=producer_id, attrib={"in": "00:00:00.000", "out": out_duration})

            # Update the previous_time to the current marker's start time
            previous_time = marker_start_time

        # Insert the new playlist after the last <playlist> and before <transition>
        all_playlists = root.findall(".//playlist")
        last_playlist = all_playlists[-1] if all_playlists else None

        if last_playlist is not None:
            index = list(root).index(last_playlist) + 1
            root.insert(index, playlist)
        else:
            # If no playlists exist, add it at the root level
            root.append(playlist)

        # Add the new playlist to the <track> section
        track_section = root.find(".//tractor")
        if track_section is not None:
            # Ensure the new track is added after the last <track> inside the <tractor>
            all_tracks = track_section.findall("./track")
            last_track = all_tracks[-1] if all_tracks else None

            new_track = ET.Element("track", producer=new_playlist_id)
            if last_track is not None:
                index = list(track_section).index(last_track) + 1
                track_section.insert(index, new_track)
            else:
                track_section.append(new_track)

        # Serialize the updated XML back to a string
        pretty_string = prettify_xml_with_no_extra_lines(root)

        # Load the updated content into the Output Preview
        self.load_output_preview(pretty_string)

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
        Adds producer elements to the output file based on the markers.
        """
        # Check if there's content in the output text box
        existing_output_content = self.output_mlt_text.get("1.0", tk.END).strip()

        if existing_output_content:
            # Use the existing content in the output preview as the base
            content = existing_output_content
        else:
            # Otherwise, load content from the .mlt file
            mlt_file = self.config.get("shortcut", None)
            if not mlt_file or not os.path.exists(mlt_file):
                print("Error: No valid .mlt file found in config.")
                return

            with open(mlt_file, "r", encoding="utf-8") as file:
                content = file.read()

        # Parse the content as XML
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
            highest_producer_id += 1  # Increment the producer ID
            producer_id = f"producer{highest_producer_id}"

            # Calculate the unique hash for this producer
            marker_name = marker.get("Name", "unknown")
            hash_input = f"{marker_name}_{datetime.utcnow().isoformat()}".encode("utf-8")
            unique_hash = hashlib.md5(hash_input).hexdigest()  # Generate a 32-character hash

            # Get the current datetime in the required format
            creation_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

            # Get the resource path
            resource_path = marker.get("Picture", "")
            if not resource_path:
                print(f"Error: Marker '{marker_name}' has no picture assigned.")
                return

            # Create the producer element
            producer = ET.Element("producer", id=producer_id, attrib={"in": "00:00:00.000", "out": "03:59:59.983"})
            ET.SubElement(producer, "property", name="length").text = "04:00:00.000"
            ET.SubElement(producer, "property", name="eof").text = "pause"
            ET.SubElement(producer, "property", name="resource").text = resource_path.replace("\\", "/")
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
            ET.SubElement(producer, "property", name="shotcut:caption").text = os.path.basename(resource_path)

            # Add the producer element before the last </playlist> or </mlt>
            playlist = root.find(".//playlist[last()]")
            if playlist is not None:
                root.insert(list(root).index(playlist), producer)

        # Serialize the updated XML back to a string
        pretty_string = prettify_xml_with_no_extra_lines(root)

        # Load the updated content into the Output Preview
        self.load_output_preview(pretty_string)

    def add_transitions(self):
        """
        Add missing or necessary transitions to the output file, ensuring proper formatting.
        """
        # Load content from the output text box or original .mlt file
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

        # Parse the .mlt file as XML
        root = ET.fromstring(content)

        # Find all tracks
        tracks = root.findall(".//track")
        existing_transitions = root.findall(".//transition")

        # Determine the highest transition ID
        highest_transition_id = 0
        for transition in existing_transitions:
            transition_id = transition.get("id", "")
            if transition_id.startswith("transition"):
                try:
                    transition_number = int(transition_id.replace("transition", ""))
                    highest_transition_id = max(highest_transition_id, transition_number)
                except ValueError:
                    pass

        # Create a set of existing (a_track, b_track) pairs to avoid duplicates
        existing_pairs = set()
        for transition in existing_transitions:
            a_track = transition.find("./property[@name='a_track']")
            b_track = transition.find("./property[@name='b_track']")
            if a_track is not None and b_track is not None:
                existing_pairs.add((a_track.text, b_track.text))

        # Add missing transitions
        for i, track in enumerate(tracks):
            for j, next_track in enumerate(tracks[i+1:], start=i+1):
                # Check if this pair of tracks already has a transition
                a_track = str(i)  # Current track index
                b_track = str(j)  # Next track index
                if (a_track, b_track) in existing_pairs:
                    continue

                # Create a new transition
                highest_transition_id += 1
                transition = ET.Element("transition", id=f"transition{highest_transition_id}")
                ET.SubElement(transition, "property", name="a_track").text = a_track
                ET.SubElement(transition, "property", name="b_track").text = b_track
                ET.SubElement(transition, "property", name="mlt_service").text = "mix"
                ET.SubElement(transition, "property", name="always_active").text = "1"
                ET.SubElement(transition, "property", name="sum").text = "1"

                # Add the transition to the root element
                root.append(transition)

        # Serialize the updated XML back to a string with proper formatting
        updated_content = prettify_xml_with_no_extra_lines(root)

        # Load the updated content into the Output Preview
        self.load_output_preview(updated_content)




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
