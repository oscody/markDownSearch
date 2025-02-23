import csv
import os

# Step 1: Load the CSV file
csv_file = "Google Passwords.csv"
passwords = []

with open(csv_file, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Assuming the CSV headers are: name, url, username, password, note
        if row.get("password"):
            passwords.append(row["password"])

# Define the exclusion list with relative paths
excluded_files = [
    "Bogle/4. Archives/Evernote/nians notebook/login.md",
    "Bogle/4. Archives/Evernote/nians notebook/clothes shopping fashion.md",
    "Bogle/4. Archives/Evernote/nians notebook/Crypto.md",
    "Bogle/4. Archives/Evernote/Imp/bills House.md"
]

# Step 2: Loop through `.md` files and search for passwords, excluding specified files
def search_passwords_in_md_files(directory, passwords):
    # Get the parent directory so that relative paths match the exclusion list
    parent_dir = os.path.dirname(directory)
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                # Compute the relative path from the parent directory
                rel_path = os.path.relpath(file_path, parent_dir)
                # Skip the file if it is in the exclusion list
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