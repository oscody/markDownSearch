import os
import xml.etree.ElementTree as ET
from datetime import datetime

def get_note_created_date(md_filepath):
    """
    Given the full path of a Markdown file, this function:
      - Extracts the folder name after 'Evernote' from the path.
      - Constructs the corresponding .enex filename from that folder name.
      - Searches the .enex file for a note with a <title> matching the Markdown file's base name.
      - Returns the note's <created> date as an ISO-formatted string.
    
    Parameters:
        md_filepath (str): Full path of the Markdown file.
          e.g. "/Users/bogle/Dev/obsidian/Bogle/4. Archives/Evernote/Dotnet/Robyn.md"
    
    Returns:
        str or None: The ISO-formatted creation date (e.g. "2023-06-09T18:50:31")
                     or None if not found.
    """
    # Ensure the provided path contains 'Evernote'
    if "Evernote" not in md_filepath:
        raise ValueError("The provided path does not contain 'Evernote'")

    # Split the path after "Evernote" to extract the folder name
    # e.g. "/Users/bogle/Dev/.../Evernote/Dotnet/Robyn.md" -> "Dotnet"
    parts = md_filepath.split("Evernote")
    remainder = parts[1].lstrip(os.sep)  # Remove any leading '/'
    folder_name = remainder.split(os.sep)[0]

    # Get the Markdown base name (e.g., "Robyn" from "Robyn.md")
    base_name = os.path.splitext(os.path.basename(md_filepath))[0]

    # Construct the full path to the .enex file in the downloads directory
    enex_search_dir = "/Users/bogle/Dev/Agent/markDownSearch/drive-download/"
    enex_filename = f"{folder_name}.enex"
    enex_filepath = os.path.join(enex_search_dir, enex_filename)

    # Parse the .enex file
    try:
        tree = ET.parse(enex_filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find {enex_filepath}")

    root = tree.getroot()

    # Iterate through each <note> to find the one with the matching <title>
    for note in root.findall("note"):
        title_elem = note.find("title")
        if title_elem is not None and title_elem.text.strip() == base_name:
            created_elem = note.find("created")
            if created_elem is not None:
                created_str = created_elem.text.strip()  # e.g., "20230609T185031Z"
                dt = datetime.strptime(created_str, "%Y%m%dT%H%M%SZ")
                return dt.isoformat()
    
    # Return None if no matching note is found
    return None

# Example usage:
md_filepath = "/Users/bogle/Dev/obsidian/Bogle/4. Archives/Evernote/Dotnet/Robyn.md"
date_str = get_note_created_date(md_filepath)
print(date_str)  # Expected output: "2023-06-09T18:50:31" (ISO formatted creation date)