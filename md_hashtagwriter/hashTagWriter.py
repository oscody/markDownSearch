import os
import re
import logging
import datetime
import difflib

# ---------------------------------------------
# CONFIGURATION
# ---------------------------------------------
input_dir = '/Users/bogle/Dev/obsidian/Bogle'
allowed_dirs = {"1. Projects", "2. Areas", "3. Resources", "4. Archives"}

writerName = "scriptinfo"

# A more descriptive variable name for the time when the script runs:
script_run_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# The .md file from which we'll read filename/hashtag pairs
markdown_hashtags_file = '/Users/bogle/Dev/Agent/markDownSearch/md_hashtagwriter/ollamaHashtagsV6.md'


# Limit how many matched files we actually process
max_files_to_process = 2

# Regex to extract filename and hashtags from lines like:
# | My Log .md | #SalsaClassCancellation #EvernoteSubscriptionUpdate |
pattern = r'\|\s*(.*?)\s*\|\s*([^|]+)\s*\|'

# ---------------------------------------------
# LOGGING CONFIG
# ---------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("script.log", mode='a'),
        logging.StreamHandler()
    ]
)

# ---------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------
def find_file_in_allowed_dirs(filename, base_path, allowed_dirs_set):
    """
    For each folder in allowed_dirs_set (e.g., '2. Areas'),
    search *all subfolders* under base_path/folder for 'filename'.
    Return the full path if found, else None.
    """
    for adir in allowed_dirs_set:
        allowed_path = os.path.join(base_path, adir)
        if not os.path.isdir(allowed_path):
            continue  # Skip if the directory doesn't exist
        
        # Walk every subdirectory inside allowed_path (infinitely deep)
        for root, dirs, files in os.walk(allowed_path):
            if filename in files:
                return os.path.join(root, filename)
    return None


def extract_frontmatter(content):
    """
    Returns a tuple (frontmatter_block, remainder).

    - If the file starts with '---', find the matching '---' line
      and return that entire block (including delimiters).
    - The remainder is anything after that frontmatter block.
    """
    lines = content.splitlines(keepends=True)

    if len(lines) > 0 and lines[0].strip() == '---':
        # Find the second '---'
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                frontmatter_block = ''.join(lines[0 : i+1])
                remainder = ''.join(lines[i+1:])
                return frontmatter_block, remainder

    # No frontmatter found
    return '', content


def replace_frontmatter(content, new_frontmatter):
    """
    - Extract any existing frontmatter from the content.
    - Return content with old frontmatter replaced by the new_frontmatter.
      If none existed, prepend it at the start.
    """
    _, remainder = extract_frontmatter(content)
    return new_frontmatter + remainder


def build_new_frontmatter(filename, hashtags, creation_date_str):
    """
    Build the desired frontmatter block as a *string* (including the '---' lines).
    """
    return (
        "---\n"
        f"name: {filename}\n"
        f"tags: {hashtags}\n"
        f"date-created: {creation_date_str}\n"
        f"script-writer: {writerName}\n"
        f"script-run-date: {script_run_time_str}\n"
        "---\n\n"
    )


def show_frontmatter_diff(old_fm, new_fm, file_path):
    """
    Show a unified diff of the old vs. new frontmatter blocks (both are strings).
    If there's no difference, returns False; else True.
    """
    old_lines = old_fm.splitlines(keepends=True)
    new_lines = new_fm.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile='Current Frontmatter',
        tofile='New Frontmatter'
    )
    diff_text = "".join(diff)

    if diff_text.strip():
        return True
    else:
        return False


def update_frontmatter(file_path, filename, hashtags):
    """
    1. Read the file's content.
    2. Extract old frontmatter, build new frontmatter.
    3. Show a diff if changed, then overwrite the file with new content.
    """
    # Get creation time (on Linux, ctime != creation time).
    creation_timestamp = os.path.getctime(file_path)
    creation_date_str = datetime.datetime.fromtimestamp(creation_timestamp).strftime('%Y-%m-%d %H:%M:%S')

    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # If the existing file itself contains "I can't" or "I cannot", skip updating
    if any(bad_str in original_content for bad_str in ["I can't", "I cannot"]):
        logging.info(f"Skipped file due to existing 'I can't' or 'I cannot' content: {file_path}")
        return

    old_fm_block, _ = extract_frontmatter(original_content)
    new_fm_block = build_new_frontmatter(filename, hashtags, creation_date_str)

    # Show diff in the log if there's any difference
    changed = show_frontmatter_diff(old_fm_block, new_fm_block, file_path)

    if changed:
        updated_content = replace_frontmatter(original_content, new_fm_block)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        logging.info(f"Updated frontmatter in: {file_path}")
    else:
        logging.info(f"No frontmatter changes for: {file_path} - Skipped.")


# ---------------------------------------------
# MAIN LOGIC
# ---------------------------------------------
def main():
    processed_count = 1

    with open(markdown_hashtags_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        if processed_count >= max_files_to_process:
            logging.info(f"Reached max_files_to_process limit ({max_files_to_process}). Stopping.")
            break

        match = re.search(pattern, line)
        if match:
            filename_raw = match.group(1).strip()   
            hashtags_raw = match.group(2).strip()

            # --- NEW CHECK: skip if the hashtags contain "I can't" or "I cannot" ---
            if any(bad_str in hashtags_raw for bad_str in ["I can't", "I cannot"]):
                logging.info(f"Skipping '{filename_raw}' because hashtags contain 'I can't' or 'I cannot'.")
                continue

            # OPTIONAL: remove '#' if you don't want them in your final tags
            hashtags_clean = " ".join(tag.lstrip('#') for tag in hashtags_raw.split())

            if not filename_raw.lower().endswith('.md'):
                logging.info(f"Line skipped (filename not ending with .md): {filename_raw}")
                continue

            file_path = find_file_in_allowed_dirs(filename_raw, input_dir, allowed_dirs)
            if file_path:
                update_frontmatter(file_path, filename_raw, hashtags_clean)
                processed_count += 1
            else:
                logging.warning(f"Could not find '{filename_raw}' in allowed directories. Skipping.")

    logging.info(f"Total files processed: {processed_count}")


if __name__ == "__main__":
    main()