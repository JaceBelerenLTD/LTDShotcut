import xml.etree.ElementTree as ET

class MediaHandler:
    """
    Handles media files such as .mlt for extracting markers and other metadata.
    """

    @staticmethod
    def extract_markers_from_file(file_path):
        """
        Simulates the extraction of markers from an .mlt file.
        For now, this function returns hard-coded markers.
        """
        # Hard-coded markers
        markers = [
    {"Number": 1, "Name": "monk", "Time": "00:01:20"},
    {"Number": 2, "Name": "wizard", "Time": "00:02:40"},
    {"Number": 3, "Name": "knight", "Time": "00:03:50"},
    {"Number": 4, "Name": "archer", "Time": "00:04:30"},
    {"Number": 5, "Name": "druid", "Time": "00:05:40"},
    {"Number": 6, "Name": "bard", "Time": "00:06:50"},
    {"Number": 7, "Name": "rogue", "Time": "00:07:20"},
    {"Number": 8, "Name": "paladin", "Time": "00:08:40"},
    {"Number": 9, "Name": "sorcerer", "Time": "00:09:50"},
    {"Number": 10, "Name": "hunter", "Time": "00:10:20"},
    {"Number": 11, "Name": "warrior", "Time": "00:11:30"},
    {"Number": 12, "Name": "priest", "Time": "00:12:40"},
    {"Number": 13, "Name": "necromancer", "Time": "00:13:50"},
    {"Number": 14, "Name": "ranger", "Time": "00:14:30"},
    {"Number": 15, "Name": "mage", "Time": "00:15:20"},
    {"Number": 16, "Name": "shaman", "Time": "00:16:40"},
    {"Number": 17, "Name": "warlock", "Time": "00:17:50"},
    {"Number": 18, "Name": "cleric", "Time": "00:18:30"},
    {"Number": 19, "Name": "alchemist", "Time": "00:19:40"},
    {"Number": 20, "Name": "assassin", "Time": "00:20:50"},
    {"Number": 21, "Name": "templar", "Time": "00:21:20"},
    {"Number": 22, "Name": "beastmaster", "Time": "00:22:30"},
    {"Number": 23, "Name": "elementalist", "Time": "00:23:40"},
    {"Number": 24, "Name": "enchanter", "Time": "00:24:50"},
    {"Number": 25, "Name": "illusionist", "Time": "00:25:30"},
    {"Number": 26, "Name": "pyromancer", "Time": "00:26:40"},
    {"Number": 27, "Name": "geomancer", "Time": "00:27:50"},
    {"Number": 28, "Name": "cryomancer", "Time": "00:28:30"},
    {"Number": 29, "Name": "spellblade", "Time": "00:29:40"},
    {"Number": 30, "Name": "berserker", "Time": "00:30:50"},
    {"Number": 31, "Name": "witch", "Time": "00:31:20"},
    {"Number": 32, "Name": "ninja", "Time": "00:32:30"},
    {"Number": 33, "Name": "samurai", "Time": "00:33:40"},
    {"Number": 34, "Name": "monk", "Time": "00:34:50"},
    {"Number": 35, "Name": "wizard", "Time": "00:35:30"},
    {"Number": 36, "Name": "knight", "Time": "00:36:40"},
    {"Number": 37, "Name": "archer", "Time": "00:37:50"},
    {"Number": 38, "Name": "druid", "Time": "00:38:30"},
    {"Number": 39, "Name": "bard", "Time": "00:39:40"},
    {"Number": 40, "Name": "rogue", "Time": "00:40:50"},
    {"Number": 41, "Name": "paladin", "Time": "00:41:20"},
    {"Number": 42, "Name": "sorcerer", "Time": "00:42:30"},
    {"Number": 43, "Name": "hunter", "Time": "00:43:40"},
    {"Number": 44, "Name": "warrior", "Time": "00:44:50"},
    {"Number": 45, "Name": "priest", "Time": "00:45:30"},
    {"Number": 46, "Name": "necromancer", "Time": "00:46:40"},
    {"Number": 47, "Name": "ranger", "Time": "00:47:50"},
    {"Number": 48, "Name": "mage", "Time": "00:48:30"},
    {"Number": 49, "Name": "shaman", "Time": "00:49:40"},
    {"Number": 50, "Name": "warlock", "Time": "00:50:50"}
]

        return markers

    @staticmethod
    def parse_mlt_file(file_path):
        """
        Parses the given .mlt file and extracts markers from its XML content.
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Example: Adjust based on the actual structure of the .mlt XML file
            markers = []
            for marker in root.findall('.//marker'):
                number = marker.get("number")  # Replace with actual attribute or tag
                name = marker.find("name").text  # Replace with actual structure
                time = marker.find("time").text  # Replace with actual structure
                markers.append({"Number": number, "Name": name, "Time": time})

            return markers
        except Exception as e:
            print(f"Error parsing .mlt file: {e}")
            return []
