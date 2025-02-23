import os
import re
from collections import Counter
import pandas as pd

def extract_links_from_file(file_path):
    """Extract all links from a Markdown file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    # Regex pattern to match Markdown links and plain URLs
    link_pattern = r"(https?://[^\s)]+)"
    return re.findall(link_pattern, content)

def count_links_in_directory(input_dir, allowed_dirs=None):
    """Count links in all Markdown files within a directory."""
    link_counter = Counter()

    for root, dirs, files in os.walk(input_dir):
        # Filter allowed directories if specified
        if allowed_dirs is not None and root == input_dir:
            dirs[:] = [d for d in dirs if d in allowed_dirs]

        for filename in files:
            if filename.lower().endswith('.md'):
                file_path = os.path.join(root, filename)
                if os.path.isfile(file_path):
                    links = extract_links_from_file(file_path)
                    link_counter.update(links)

    return link_counter

def create_link_usage_table(link_counter, output_file):
    """Create a table of links and their usage count."""
    # Convert the counter to a DataFrame for better representation
    df = pd.DataFrame(link_counter.items(), columns=['Link', 'Usage Count'])
    df = df.sort_values(by='Usage Count', ascending=False).reset_index(drop=True)

    # Write the table to a CSV file
    df.to_csv(output_file, index=False)
    print(f"CSV file written to: {output_file}")
    return df

if __name__ == '__main__':
    input_dir = '/Users/bogle/Dev/obsidian/Bogle'
    allowed_dirs = {"1. Projects", "2. Areas", "3. Resources", "4. Archives"}

    
    # Count links in the directory
    link_counter = count_links_in_directory(input_dir, allowed_dirs)

    # Define output CSV file path in the same directory as the script
    output_file = os.path.join(os.path.dirname(__file__), 'link_usage_report.csv')

    # Generate table and write CSV
    link_table = create_link_usage_table(link_counter, output_file)

    # Display table
    print(link_table)