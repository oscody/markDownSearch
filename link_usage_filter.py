# not working 

import pandas as pd
from urllib.parse import urlparse

# Load the CSV file
file_path = 'link_usage_report.csv'  # Replace with your actual file path
try:
    data = pd.read_csv(file_path, header=None, names=['url'])
    print(f"Loaded {len(data)} rows from the file.")
except Exception as e:
    print(f"Error reading the file: {e}")
    exit()

# Inspect the first few rows
print("Preview of data:")
print(data.head())

# Extract the base URL (scheme + netloc)
def get_base_url(url):
    try:
        if pd.isna(url) or not isinstance(url, str):
            raise ValueError("Invalid or non-string URL.")
        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            raise ValueError(f"Missing domain in URL: {url}")
        return f"{parsed_url.scheme}://{parsed_url.netloc}"
    except Exception as e:
        print(f"Error parsing URL '{url}': {e}")
        return None

# Apply the function to extract base URLs
data['base_url'] = data['url'].apply(lambda x: get_base_url(x))

# Log invalid URLs
invalid_urls = data[data['base_url'].isna()]
print("Invalid URLs detected:")
print(invalid_urls)

# Save invalid URLs to a separate CSV file
invalid_urls_file = 'invalid_urls_report.csv'
try:
    invalid_urls.to_csv(invalid_urls_file, index=False)
    print(f"Invalid URLs saved to '{invalid_urls_file}'")
except Exception as e:
    print(f"Error saving invalid URLs file: {e}")

# Count the occurrences of each base URL
base_url_counts = data['base_url'].value_counts().reset_index()
base_url_counts.columns = ['Link', 'Usage Count']

# Check if the counts are correct
if base_url_counts.empty:
    print("No valid base URLs were found. Please check the input data.")
else:
    print("Preview of base URL counts:")
    print(base_url_counts.head())

# Save the base URL counts to a CSV file
output_file_path = 'base_url_counts_report.csv'
try:
    base_url_counts.to_csv(output_file_path, index=False)
    print(f"Base URL counts saved to '{output_file_path}'")
except Exception as e:
    print(f"Error saving the file: {e}")