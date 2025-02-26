import sqlite3
import os
from datetime import datetime
import json

def initialize_db(db_path="obsidian_index.db"):
    conn = sqlite3.connect(db_path)
    return conn

def add_file(conn, file_path , metadata):
    """Add a new file or update an existing one if renamed."""
    cursor = conn.cursor()
    file_name = os.path.basename(file_path)


    date_created = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
        
    cursor.execute("""
        INSERT INTO files (name, path, date_created, deleted , metadata)
        VALUES (?, ?, ?, 0)
    """, (file_name, file_path, date_created))
    
    conn.commit()
    conn.close()


def check_for_ai_suggestions(db_path="obsidian_index.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(files)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if "ai_existing_tags" not in existing_columns:
        cursor.execute("ALTER TABLE files ADD COLUMN ai_existing_tags TEXT")

    if "ai_new_tags" not in existing_columns:
        cursor.execute("ALTER TABLE files ADD COLUMN ai_new_tags TEXT")

    if "updated" not in existing_columns:
        cursor.execute("ALTER TABLE files ADD COLUMN updated DATETIME")

    conn.commit()
    conn.close()



def add_file_with_tags(file_path , existing_tags, new_tags , update_time, db_path="obsidian_index.db",):
    """Add a new file or update an existing one if renamed."""
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    file_name = os.path.basename(file_path)

    date_created = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d %H:%M:%S")

    existing_tags = ', '.join(existing_tags.values()) if isinstance(existing_tags, dict) else str(existing_tags)
    new_tags = ', '.join(new_tags.values()) if isinstance(new_tags, dict) else str(new_tags)

        
    cursor.execute("""
        INSERT INTO files (name, path, date_created, deleted , ai_existing_tags , ai_new_tags, updated)
        VALUES (?, ?, ?, 0, ?, ?, ?)
    """, (file_name, file_path, date_created , existing_tags , new_tags , update_time))

    conn.commit()
    conn.close()



def get_tag_by_file(file_path, db_path="obsidian_index.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    file_name = os.path.basename(file_path)

    cursor.execute("""
        SELECT ai_existing_tags, ai_new_tags
        FROM files
        WHERE path = ? AND name = ?
    """, (file_path, file_name))

    row = cursor.fetchone()

    conn.close()

    if row:
        existing_tags = json.loads(row[0]) if row[0] else {}
        new_tags = json.loads(row[1]) if row[1] else {}
        return existing_tags, new_tags
    else:
        return {}, {}
    

def select_all_db( db_path="obsidian_index.db"):
    conn = sqlite3.connect(db_path)
    # Query the database for file paths (assuming 'path' is stored in the DB)
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM files WHERE deleted = 0")
    existing_files = {row[0] for row in cursor.fetchall()}
    return existing_files