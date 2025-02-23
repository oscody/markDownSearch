import os
import sqlite3
import hashlib
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
            metadata TEXT,
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
    # Using a dictionary keyed by file_hash for quick lookup
    existing = {}
    for row in rows:
        file_id, path, name, file_hash = row
        if file_hash:
            existing[file_hash] = {'id': file_id, 'path': path, 'name': name}
    return existing

def add_or_update_file(conn, file_path):
    """Add a new file or update an existing one if renamed."""
    cursor = conn.cursor()
    file_hash = compute_file_hash(file_path)
    if file_hash is None:
        return  # Skip files that couldn’t be hashed
    file_name = os.path.basename(file_path)
    date_created = datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
    
    existing_files = get_existing_files(conn)
    
    if file_hash in existing_files:
        # File exists (even if renamed), update path and name if necessary.
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
        # New file; insert it.
        cursor.execute("""
            INSERT INTO files (name, file, path, date_created, file_hash, deleted)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (file_name, None, file_path, date_created, file_hash))
        conn.commit()
        print(f"Added new file: {file_path}")

def scan_directory(conn, directory):
    """Scan the directory for files and process them."""
    # Only allow these top-level directories relative to the target directory.
    allowed_dirs = {"1. Projects", "2. Areas", "3. Resources", "4. Archives"}
    
    # Keep track of files seen during this scan (by file_hash)
    seen_hashes = set()
    
    for root, dirs, files in os.walk(directory):
        # Determine if the current directory is within allowed directories.
        # Get the relative path from the target directory.
        relative_root = os.path.relpath(root, directory)
        if relative_root != ".":
            # Grab the top-level folder in the relative path.
            top_dir = relative_root.split(os.sep)[0]
            if top_dir not in allowed_dirs:
                continue  # Skip this directory if it's not allowed.
        
        for file in files:
            # Only process markdown files.
            if not file.endswith(".md"):
                continue
            full_path = os.path.join(root, file)
            file_hash = compute_file_hash(full_path)
            if file_hash:
                seen_hashes.add(file_hash)
                add_or_update_file(conn, full_path)
    
    # Mark files as deleted if they were not seen in the current scan.
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_hash, path FROM files WHERE deleted = 0")
    for file_id, file_hash, path in cursor.fetchall():
        if file_hash not in seen_hashes:
            cursor.execute("UPDATE files SET deleted = 1 WHERE id = ?", (file_id,))
            conn.commit()
            print(f"Marked file as deleted: {path}")

def main():
    db_path = "files_sql.db"
    # Replace with your target directory.
    directory_to_scan = "/Users/bogle/Dev/obsidian/Bogle"
    conn = initialize_db(db_path)
    scan_directory(conn, directory_to_scan)
    conn.close()

if __name__ == '__main__':
    main()