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

# print(f"passwords-{passwords}")

# Step 2: Loop through `.md` files and search for passwords
def search_passwords_in_md_files(directory, passwords):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
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