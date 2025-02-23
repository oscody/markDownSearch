import os

# Define the allowed top-level directories
allowed_dirs = {"1. Projects", "2. Areas", "3. Resources", "4. Archives"}

# Specify the starting directory and the output Markdown filename.
START_DIRECTORY = "/Users/bogle/Dev/obsidian/Bogle"
OUTPUT_FILENAME = "file_list.md"

def list_md_files(start_directory, allowed_dirs):
    """
    Recursively collects the full paths of all Markdown (.md) files
    located within allowed top-level subdirectories of the start_directory.
    """
    md_file_list = []
    for dirpath, dirnames, filenames in os.walk(start_directory):
        # Determine the relative path from the starting directory.
        rel_path = os.path.relpath(dirpath, start_directory)
        if rel_path == ".":
            # Only traverse directories that are in the allowed set.
            dirnames[:] = [d for d in dirnames if d in allowed_dirs]
            continue
        # Collect .md files from the allowed directories (and their subdirectories).
        for filename in filenames:
            if filename.lower().endswith(".md"):
                full_path = os.path.join(dirpath, filename)
                md_file_list.append(full_path)
    return md_file_list

def write_to_markdown(file_list, md_filename):
    """
    Writes the file list into a Markdown file with a header and bullet points.
    """
    with open(md_filename, 'w') as md_file:
        md_file.write("# List of Markdown Files\n\n")
        for file in file_list:
            md_file.write(f"- {file}\n")
    print(f"Markdown file list has been written to {md_filename}")

if __name__ == "__main__":
    md_files = list_md_files(START_DIRECTORY, allowed_dirs)
    write_to_markdown(md_files, OUTPUT_FILENAME)