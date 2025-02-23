import csv
import os

# List of passwords to exclude (in lowercase)
excluded_passwords = ["bogle", "***", "2793", "11412", "123456"]

# Step 1: Load the CSV files, excluding any passwords in the excluded_passwords list
csv_files = ["oneil Chrome Passwords.csv", "work Chrome Passwords.csv", "Google Passwords.csv"]
passwords = []

for csv_file in csv_files:
    try:
        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Assuming the CSV headers include: name, url, username, password, note
                password_value = row.get("password")
                # Exclude the password if it exists in the excluded_passwords list (case-insensitive)
                if password_value and password_value.lower() not in excluded_passwords:
                    passwords.append(password_value)
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")

# Define the exclusion list with relative paths for markdown files
excluded_files = [
    "Bogle/4. Archives/Evernote/nians notebook/login.md",
    "Bogle/4. Archives/Evernote/nians notebook/clothes shopping fashion.md",
    "Bogle/4. Archives/Evernote/nians notebook/Crypto.md",
    "Bogle/4. Archives/Evernote/Imp/bills House.md",
    "Bogle/4. Archives/Evernote/Fam/not look Please do not look Please do not look Please do not look Please do not look Please do not look Please do not look Please dedo not look Please do not l.md",
    "Bogle/4. Archives/Evernote/nians notebook/robyn.md",
    "Bogle/4. Archives/Evernote/nians notebook/Learn akashx Trading.md"
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