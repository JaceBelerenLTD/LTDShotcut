import xml.etree.ElementTree as ET

class MediaHandler:
    """
    Handles media files such as .mlt for extracting markers and other metadata.
    """
import xml.etree.ElementTree as ET

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
                    "Time": marker_element.find("property[@name='start']").text,
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