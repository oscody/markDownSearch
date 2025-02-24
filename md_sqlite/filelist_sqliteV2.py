import os
import sqlite3
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime

def initialize_db(db_path="files.db"):
    """Initialize the SQLite database and create the table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            date_created DATETIME,
            file_hash TEXT,
            deleted BOOLEAN DEFAULT 0,
            metadata TEXT
        );
    """)
    conn.commit()
    return conn

def compute_file_hash(file_path):
    """Compute SHA256 hash of the file's contents."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def get_existing_files(conn):
    """Retrieve a dictionary of existing file records keyed by file_hash."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, path, name, file_hash FROM files WHERE deleted = 0")
    rows = cursor.fetchall()
    existing = {}
    for row in rows:
        file_id, path, name, file_hash = row
        if file_hash:
            existing[file_hash] = {'id': file_id, 'path': path, 'name': name}
    return existing

def get_note_created_date(md_filepath):
    """
    Given the full path of a Markdown file in "4. Archives", this function:
      - Extracts the folder name after 'Evernote' if present, or immediately after '4. Archives' otherwise.
      - Constructs the corresponding .enex filename from that folder name.
      - Searches the .enex file for a note with a <title> matching the Markdown file's base name.
      - Returns the note's <created> date as an ISO-formatted string.
    
    If the .enex file is not found or no matching note is located, it falls back to the file's creation date.
    
    Parameters:
        md_filepath (str): Full path of the Markdown file.
          e.g. "/Users/bogle/Dev/obsidian/Bogle/4. Archives/Evernote/Dotnet/Robyn.md"
               "/Users/bogle/Dev/obsidian/Bogle/4. Archives/AI/SomeNote.md"
    
    Returns:
        str: The ISO-formatted creation date.
    """
    folder_name = None
    if "Evernote" in md_filepath:
        parts = md_filepath.split("Evernote")
        remainder = parts[1].lstrip(os.sep)
        folder_name = remainder.split(os.sep)[0]
    elif "4. Archives" in md_filepath:
        parts = md_filepath.split("4. Archives")
        remainder = parts[1].lstrip(os.sep)
        folder_name = remainder.split(os.sep)[0]
    else:
        # Fallback if neither Evernote nor 4. Archives is in the path.
        return datetime.fromtimestamp(os.path.getctime(md_filepath)).isoformat()

    base_name = os.path.splitext(os.path.basename(md_filepath))[0]
    enex_search_dir = "/Users/bogle/Dev/Agent/markDownSearch/drive-download/"
    enex_filename = f"{folder_name}.enex"
    enex_filepath = os.path.join(enex_search_dir, enex_filename)

    try:
        tree = ET.parse(enex_filepath)
    except FileNotFoundError:
        print(f"File NotF ound Error {md_filepath}")
        return datetime.fromtimestamp(os.path.getctime(md_filepath)).isoformat()

    root = tree.getroot()

    for note in root.findall("note"):
        title_elem = note.find("title")
        if title_elem is not None and title_elem.text.strip() == base_name:
            created_elem = note.find("created")
            if created_elem is not None:
                created_str = created_elem.text.strip()  # e.g., "20230609T185031Z"
                dt = datetime.strptime(created_str, "%Y%m%dT%H%M%SZ")
                return dt.isoformat()

    # Fallback if no matching note is found
    return datetime.fromtimestamp(os.path.getctime(md_filepath)).isoformat()

def add_or_update_file(conn, file_path):
    """Add a new file or update an existing one if renamed."""
    cursor = conn.cursor()
    file_hash = compute_file_hash(file_path)
    if file_hash is None:
        print(f"Skip files that couldn’t be hashed {file_path}")
        return  # Skip files that couldn’t be hashed
    file_name = os.path.basename(file_path)

    # Determine date_created based on file location
    if "4. Archives" in file_path:
        note_date = get_note_created_date(file_path)
        date_created = note_date
    else:
        date_created = datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
    
    existing_files = get_existing_files(conn)
    
    if file_hash in existing_files:
        record = existing_files[file_hash]
        if record['path'] != file_path or record['name'] != file_name:
            cursor.execute("""
                UPDATE files 
                SET path = ?, name = ?, date_created = ?
                WHERE id = ?
            """, (file_path, file_name, date_created, record['id']))
            conn.commit()
            print(f"Updated file record for: {file_path}")
    else:
        cursor.execute("""
            INSERT INTO files (name, path, date_created, file_hash, deleted)
            VALUES (?, ?, ?, ?, 0)
        """, (file_name, file_path, date_created, file_hash))
        conn.commit()
        print(f"Added new file: {file_path}")

def scan_directory(conn, directory):
    """Scan the directory for files and process them."""
    allowed_dirs = {"1. Projects", "2. Areas", "3. Resources", "4. Archives"}
    seen_hashes = set()
    
    for root, dirs, files in os.walk(directory):
        relative_root = os.path.relpath(root, directory)
        if relative_root != ".":
            top_dir = relative_root.split(os.sep)[0]
            if top_dir not in allowed_dirs:
                continue
        
        for file in files:
            if not file.endswith(".md"):
                continue
            full_path = os.path.join(root, file)
            file_hash = compute_file_hash(full_path)
            if file_hash:
                seen_hashes.add(file_hash)
                add_or_update_file(conn, full_path)
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_hash, path FROM files WHERE deleted = 0")
    for file_id, file_hash, path in cursor.fetchall():
        if file_hash not in seen_hashes:
            cursor.execute("UPDATE files SET deleted = 1 WHERE id = ?", (file_id,))
            conn.commit()
            print(f"Marked file as deleted: {path}")

def main():
    db_path = "files_sql_date.db"
    directory_to_scan = "/Users/bogle/Dev/obsidian/Bogle"
    conn = initialize_db(db_path)
    scan_directory(conn, directory_to_scan)
    conn.close()

if __name__ == '__main__':
    main()