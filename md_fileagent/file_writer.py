import glob
import os


base_dir = "/Users/bogle/Dev/obsidian/Bogle"


def get_file_path(file_path):

    # If the path is relative, convert it to absolute
    if not os.path.isabs(file_path):
        file_path = os.path.join(base_dir, file_path)
    
    return file_path

def get_filename(file_path):
    return os.path.basename(file_path)

def update_file(file_path , updated_content):
    
    file_path = get_file_path(file_path)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    return True


def open_filefile_path(file_path):
    try:

        file_path = get_file_path(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return ""
    

def get_file_content(file_path):
    """Read and return the content of a file. Returns an empty string if reading fails."""
    try:

        file_path = get_file_path(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def get_all_files(directory):
        # Get all Markdown file paths recursively (efficient since glob is implemented in C)
    return set(glob.glob(os.path.join(directory, '**', '*.md'), recursive=True))