import json
import os

# Step 1: Load the JSON file
json_file = "bitwarden_export_20241207182233.json"

with open(json_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# Step 2: Extract passwords from the JSON structure
passwords = [item["login"]["password"] for item in data["items"] if item.get("login") and item["login"].get("password")]

# Exclusion list (relative to the parent directory of the search folder)
excluded_files = [
    "Bogle/4. Archives/Evernote/nians notebook/login.md",
    "Bogle/4. Archives/Evernote/nians notebook/clothes shopping fashion.md",
    "Bogle/4. Archives/Evernote/nians notebook/Crypto.md",
    "Bogle/4. Archives/Evernote/Imp/bills House.md",
    "Bogle/.trash",
]

# Step 3: Loop through `.md` files and search for passwords, excluding specified files
def search_passwords_in_md_files(directory, passwords):
    # Calculate parent directory so that relative paths match the exclusion list
    parent_dir = os.path.dirname(directory)
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                # Get the relative path from the parent of the search directory
                rel_path = os.path.relpath(file_path, parent_dir)
                # Skip file if it is in the exclusion list
                if rel_path in excluded_files:
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for password in passwords:
                        if password in content:
                            print(f"Password found in file: {file_path}")
                            print(f"Password: {password}\n")

# Specify the directory containing the `.md` files
directory_to_search = "/Users/bogle/Dev/obsidian/Bogle"

if not os.path.exists(directory_to_search):
    print(f"Directory does not exist: {directory_to_search}")
else:
    print(f"Directory found: {directory_to_search}")

# Call the function
search_passwords_in_md_files(directory_to_search, passwords)