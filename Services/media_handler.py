import os
import xml.etree.ElementTree as ET

class MediaHandler:
    # Existing functions...

    def process_and_export_mlt(self, input_file_path, output_folder, modifications):
        """
        Processes the given .mlt file and exports it to the specified folder.

        Args:
            input_file_path (str): Path to the input .mlt file.
            output_folder (str): Path to the output folder for the modified file.
            modifications (dict): A dictionary of modifications to apply.

        Returns:
            str: Path to the exported .mlt file.
        """
        try:
            # Parse the input file
            tree = ET.parse(input_file_path)
            root = tree.getroot()

            # Apply modifications (example: change markers or other properties)
            for key, value in modifications.items():
                element = root.find(f".//{key}")
                if element is not None:
                    element.text = value

            # Ensure the output folder exists
            os.makedirs(output_folder, exist_ok=True)

            # Generate output file path
            output_file_path = os.path.join(output_folder, os.path.basename(input_file_path))

            # Write the modified XML to the output file
            tree.write(output_file_path, encoding="utf-8", xml_declaration=True)
            print(f"Exported modified .mlt file to {output_file_path}")
            return output_file_path
        except Exception as e:
            print(f"An error occurred during processing: {e}")
            return None
class MediaHandler:
    def extract_markers_from_file(self, file_path):
        """
        Extracts markers from the provided .mlt file.

        Args:
            file_path (str): Path to the .mlt file.

        Returns:
            list: A list of dictionaries containing marker details.
        """
        try:
            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Locate the markers section
            markers_element = root.find(".//properties[@name='shotcut:markers']")
            if not markers_element:
                print("No markers found in the file.")
                return []

            # Extract each marker's details
            markers = []
            for index, marker_element in enumerate(markers_element.findall("properties")):
                marker = {
                    "Number": index + 1,
                    "Name": marker_element.find("property[@name='text']").text,
                    "StartTime": marker_element.find("property[@name='start']").text,
                    "EndTime": marker_element.find("property[@name='end']").text if marker_element.find("property[@name='end']") is not None else "",
                    "Color": marker_element.find("property[@name='color']").text,
                    "Picture": "",  # Default empty
                    "Video": ""    # Default empty
                }
                markers.append(marker)

            print(f"Extracted {len(markers)} markers with colors.")
            return markers

        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return []
        except Exception as e:
            print(f"An error occurred while extracting markers: {e}")
            return []
        
        