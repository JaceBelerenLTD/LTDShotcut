import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk  # Import tkinter for `tk.END`
from tkinter import messagebox
import os
import json
import difflib
from ttkbootstrap.scrolled import ScrolledText



class ExportManager:
    def __init__(self, parent):
        self.parent = parent

        # Create the Export Manager window
        self.window = ttk.Toplevel(parent)
        self.window.title("Export Manager")
        self.window.geometry("2000x1200")
        self.config = self.load_config()

        # Set up the UI layout
        self.setup_ui()

    def highlight_differences(self):
        """Highlight differences between the original .mlt file and the output preview."""
        mlt_file = self.config.get("shortcut", None)
        if not mlt_file or not os.path.exists(mlt_file):
            ttk.Messagebox.show_error("Error", "No valid .mlt file found in config.")
            return

        try:
            # Read the original content
            with open(mlt_file, "r", encoding="utf-8") as file:
                original_content = file.readlines()

            # Get the output preview content
            output_content = self.output_mlt_text.get("1.0", "end").strip().splitlines()

            # Use difflib to compare the two
            differ = difflib.Differ()
            diff_result = list(differ.compare(original_content, output_content))

            # Clear the output text box
            self.output_mlt_text.delete("1.0", "end")

            # Display differences with highlights
            for line in diff_result:
                if line.startswith("+ "):  # Added lines
                    self.output_mlt_text.insert("end", line + "\n", "added")
                elif line.startswith("- "):  # Removed lines
                    self.output_mlt_text.insert("end", line + "\n", "removed")
                elif line.startswith("? "):  # Highlight line differences
                    self.output_mlt_text.insert("end", line + "\n", "changed")
                else:  # Unchanged lines
                    self.output_mlt_text.insert("end", line + "\n")

            # Configure tags for highlighting
            self.output_mlt_text.tag_configure("added", background="lightgreen")
            self.output_mlt_text.tag_configure("removed", background="lightcoral")
            self.output_mlt_text.tag_configure("changed", background="yellow")

        except Exception as e:
            ttk.Messagebox.show_error("Error", f"Failed to highlight differences:\n{e}")

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

    def add_pictures(self):
        """Add 'PictureAdded' to the end of the existing content in the output text box or the original .mlt file."""
        # Check if there's content in the output text box
        existing_output_content = self.output_mlt_text.get("1.0", tk.END).strip()

        # If output text box has content, append 'PictureAdded' to it
        if existing_output_content:
            updated_content = existing_output_content.rstrip() + "\nadd_pictures"
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

                # Append 'PictureAdded' to the file content
                updated_content = content.rstrip() + "\nadd_pictures"

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while adding pictures:\n{e}")
                return

        # Display the updated content in the Output Preview
        self.load_output_preview(updated_content)


    def add_buttons(self, left_frame, right_frame):
        """Add buttons under the textboxes."""
        # Button frame for the left side
        left_button_frame = ttk.Frame(left_frame)
        left_button_frame.pack(fill="x", pady=10)

        # Add buttons for the left side
        ttk.Button(left_button_frame, text="Add Transitions", bootstyle="primary", command=self.add_transitions).pack(side="left", expand=True, padx=5)
        ttk.Button(left_button_frame, text="Add Pictures", bootstyle="secondary", command=self.add_pictures).pack(side="left", expand=True, padx=5)
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
        ttk.Messagebox.show_info(title="Message", message=message)

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
            ttk.Messagebox.show_error("Export Error", "Export folder is not set or does not exist.")
            return

        # Get the content of the output preview
        output_content = self.output_mlt_text.get("1.0", ttk.END).strip()
        if not output_content:
            ttk.Messagebox.show_error("Export Error", "Output content is empty.")
            return

        # Define the export file path
        export_file_path = os.path.join(export_folder, "exported_file.mlt")
        try:
            with open(export_file_path, "w", encoding="utf-8") as file:
                file.write(output_content)
            ttk.Messagebox.show_info("Export Successful", f"File successfully exported to:\n{export_file_path}")
        except Exception as e:
            ttk.Messagebox.show_error("Export Error", f"Failed to export the file:\n{e}")


if __name__ == "__main__":
    # For testing purposes only
    app = ttk.Window(themename="flatly")
    ExportManager(app)
    app.mainloop()
