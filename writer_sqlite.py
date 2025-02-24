import os
import re
import logging
import datetime
import difflib
import sqlite3
import sys

# ---------------------------------------------
# CONFIGURATION
# ---------------------------------------------
input_dir = '/Users/bogle/Dev/obsidian/Bogle'
allowed_dirs = {"1. Projects", "2. Areas", "3. Resources", "4. Archives"}

writerName = "scriptinfo"
script_run_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Set to a number to limit files, or to None to process all files
# max_files_to_process = 20   # or set to None for unlimited processing

max_files_to_process = None  # or set to None for unlimited processing


# test_target = '/Users/bogle/Dev/obsidian/Bogle/2. Areas/'
test_target = None
# test_target = sys.argv[1] if len(sys.argv) > 1 else None

# SQLite DB file path
sqlite_db_path = "obsidian_index.db"

# ---------------------------------------------
# LOGGING CONFIG
# ---------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app_write.log", mode='a'),
        logging.StreamHandler()
    ]
)

# ---------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------
def find_file_in_allowed_dirs(filename, base_path, allowed_dirs_set):
    for adir in allowed_dirs_set:
        allowed_path = os.path.join(base_path, adir)
        if not os.path.isdir(allowed_path):
            continue
        for root, dirs, files in os.walk(allowed_path):
            if filename in files:
                return os.path.join(root, filename)
    return None

def extract_frontmatter(content):
    lines = content.splitlines(keepends=True)
    if len(lines) > 0 and lines[0].strip() == '---':
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                frontmatter_block = ''.join(lines[0 : i+1])
                remainder = ''.join(lines[i+1:])
                return frontmatter_block, remainder
    return '', content

def replace_frontmatter(content, new_frontmatter):
    _, remainder = extract_frontmatter(content)
    return new_frontmatter + remainder

def build_new_frontmatter(filename, creation_date_str):
    return (
        "---\n"
        f"name: {filename}\n"
        f"tags: {''}\n"
        f"date-created: {creation_date_str}\n"
        f"script-writer: {writerName}\n"
        f"script-run-date: {script_run_time_str}\n"
        "---\n\n"
    )

def show_frontmatter_diff(old_fm, new_fm, file_path):
    old_lines = old_fm.splitlines(keepends=True)
    new_lines = new_fm.splitlines(keepends=True)
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile='Current Frontmatter',
        tofile='New Frontmatter'
    )
    diff_text = "".join(diff)
    return bool(diff_text.strip())

def get_date_created_from_db(filename, file_path, db_path=sqlite_db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date_created FROM files WHERE name = ? AND path = ? AND deleted = 0",
        (filename, file_path)
    )
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return row[0]
    return None

def update_frontmatter(file_path, filename):
    date_created_db = get_date_created_from_db(filename, file_path)
    if date_created_db is None:
        creation_timestamp = os.path.getctime(file_path)
        creation_date_str = datetime.datetime.fromtimestamp(creation_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    else:
        creation_date_str = date_created_db

    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # # Skip files with specific phrases
    # if any(bad_str in original_content for bad_str in ["I can't", "I cannot"]):
    #     logging.info(f"Skipped file due to 'I can't' or 'I cannot' content: {file_path}")
    #     return False

    old_fm_block, _ = extract_frontmatter(original_content)
    new_fm_block = build_new_frontmatter(filename, creation_date_str)
    changed = show_frontmatter_diff(old_fm_block, new_fm_block, file_path)

    if changed:
        updated_content = replace_frontmatter(original_content, new_fm_block)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        logging.info(f"Updated frontmatter in: {file_path}")
        return True
    else:
        logging.info(f"No frontmatter changes for: {file_path} - Skipped.")
        return False

def get_all_files_from_db(db_path=sqlite_db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, path FROM files WHERE deleted = 0")
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------------------------------------------
# MAIN LOGIC
# ---------------------------------------------
def main():
    processed_count = 0
    update_count = 0

    # TEST MODE: if a specific file or folder is provided, use that exclusively.
    if test_target is not None:
        logging.info(f"Running in test mode using test_target: {test_target}")
        if os.path.isfile(test_target):
            files_to_process = [(os.path.basename(test_target), test_target)]
        elif os.path.isdir(test_target):
            files_to_process = []
            for root, dirs, files in os.walk(test_target):
                for file in files:
                    if file.lower().endswith('.md'):
                        files_to_process.append((file, os.path.join(root, file)))
        else:
            logging.error(f"Test target is neither a file nor a directory: {test_target}")
            return

        for filename, file_path in files_to_process:
            processed_count += 1
            if update_frontmatter(file_path, filename):
                update_count += 1
            if max_files_to_process is not None and processed_count >= max_files_to_process:
                logging.info(f"Reached max_files_to_process limit ({max_files_to_process}) in test mode. Stopping.")
                break

    else:
        # Normal mode: attempt to use the SQLite DB list first.
        files_from_db = get_all_files_from_db()
        if files_from_db:
            logging.info("Using SQLite DB file list to update frontmatter.")
            for filename, file_path in files_from_db:
                # Apply allowed_dirs filtering
                relative_root = os.path.relpath(file_path, input_dir)
                if relative_root != ".":
                    top_dir = relative_root.split(os.sep)[0]
                    if top_dir not in allowed_dirs:
                        continue

                processed_count += 1
                if update_frontmatter(file_path, filename):
                    update_count += 1
                if max_files_to_process is not None and processed_count >= max_files_to_process:
                    logging.info(f"Reached max_files_to_process limit ({max_files_to_process}). Stopping.")
                    break
        else:
            logging.info("No file records found in the SQLite DB. Scanning allowed directories.")
            for root_dir, dirs, files in os.walk(input_dir):
                relative_root = os.path.relpath(root_dir, input_dir)
                if relative_root != ".":
                    top_dir = relative_root.split(os.sep)[0]
                    if top_dir not in allowed_dirs:
                        continue

                for file in files:
                    if not file.lower().endswith('.md'):
                        continue
                    full_path = os.path.join(root_dir, file)
                    processed_count += 1
                    if update_frontmatter(full_path, file):
                        update_count += 1
                    if max_files_to_process is not None and processed_count >= max_files_to_process:
                        logging.info(f"Reached max_files_to_process limit ({max_files_to_process}). Stopping.")
                        break
                if max_files_to_process is not None and processed_count >= max_files_to_process:
                    break

    logging.info(f"Total files processed: {processed_count}")
    logging.info(f"Total files updated: {update_count}")

if __name__ == "__main__":
    main()