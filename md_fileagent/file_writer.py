import glob
import os


def get_filename(file_path):
    return os.path.basename(file_path)

def update_file(file_path , updated_content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    return True


def open_filefile_path(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return ""
    

def get_file_content(file_path):
    """Read and return the content of a file. Returns an empty string if reading fails."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def get_all_files(directory):
        # Get all Markdown file paths recursively (efficient since glob is implemented in C)
    return set(glob.glob(os.path.join(directory, '**', '*.md'), recursive=True))