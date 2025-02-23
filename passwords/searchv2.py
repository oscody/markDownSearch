import json
import os

# Step 1: Load the JSON file
json_file = "bitwarden_export_20250123182705.json"

with open(json_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# Step 2: Extract passwords from the JSON structure
passwords = [
    item["login"]["password"]
    for item in data["items"]
    if item.get("login") and item["login"].get("password")
]

# Step 3: Loop through `.md` files and search for passwords, compiling a list of files
def search_passwords_in_md_files(directory, passwords):
    files_with_passwords = set()  # use a set to avoid duplicate file entries
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        for password in passwords:
                            if password in content:
                                files_with_passwords.add(file_path)
                                break  # break after the first match in the file
                except Exception as e:
                    print(f"Could not read file {file_path}: {e}")
    return list(files_with_passwords)

# Specify the directory containing the `.md` files
directory_to_search = "/Users/bogle/Dev/obsidian/Bogle"

if not os.path.exists(directory_to_search):
    print(f"Directory does not exist: {directory_to_search}")
else:
    print(f"Directory found: {directory_to_search}")

# Call the function and get the compiled list of files
compiled_files = search_passwords_in_md_files(directory_to_search, passwords)

# Print the compiled list
print("Compiled list of files with passwords:")
for file in compiled_files:
    print(file)