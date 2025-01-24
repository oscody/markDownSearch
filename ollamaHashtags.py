import os
import tiktoken
import ollama
import re

# Define the input directory containing your top-level folders
input_dir = '/Users/bogle/Dev/gitcode/chatgpt-markdown/outputv2'

# Define the allowed top-level directories
allowed_dirs = {"1. Projects", "2. Areas", "3. Resources", "4. Archives"}

# Specify the AI model to use
model_name = "llama3.2"

ollama_client = ollama.Client()

MAX_CONTEXT_LENGTH = 2048
DESIRED_COMPLETION_TOKENS = 150

# Function to count tokens using tiktoken
def count_tokens(text, model="cl100k_base"):
    encoding = tiktoken.get_encoding(model)
    return len(encoding.encode(text))

prompt_template = """Please analyze the following text and strictly follow these instructions:

1. Identify exactly 5
2. Output only these 5  hashtags on a single line, separated by a single space.
3. Do not include any additional text, commentary, formatting, line breaks, or punctuation beyond the 3 hashtags.
4. Each hashtag must start immediately with '#' followed directly by the word or phrase (no space after '#'). For example: #ExampleHashtag.
5. Each hashtag must be a single continuous word or phrase with no internal spaces.

Text to analyze:
{}
"""

file_count = 0
file_limit = 20
updated_files = []

# Recursively walk through directories
for root, dirs, files in os.walk(input_dir):
    # Prune directories so that at the top level we only descend into allowed_dirs
    if root == input_dir:
        dirs[:] = [d for d in dirs if d in allowed_dirs]

    for filename in files:
        # Only process .md files
        if not filename.lower().endswith('.md'):
            continue

        if file_count >= file_limit:
            break

        file_path = os.path.join(root, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()

            # Construct the initial prompt
            prompt = prompt_template.format(content)

            # Count tokens in the prompt
            prompt_tokens = count_tokens(prompt)

            # Truncate content if needed
            while prompt_tokens + DESIRED_COMPLETION_TOKENS > MAX_CONTEXT_LENGTH:
                truncate_length = int(len(content) * 0.9)
                content = content[:truncate_length]
                prompt = prompt_template.format(content)
                prompt_tokens = count_tokens(prompt)

            messages = [
                {"role": "system", "content": "You are a reliable, concise, and compliant assistant who consistently follows the user's instructions and policies."},
                {"role": "user", "content": prompt}
            ]

            response = ollama_client.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": 0.2,
                    "top_p": 0.5
                }
            )

            # Extract the summary (hashtags) from the response
            summary = response['message']['content'].strip()

            # Replace occurrences of "# " (hash followed by space) with "#"
            summary = re.sub(r'#\s+', '#', summary)
            
            # Prepend the AI generated hashtag line to the file content
            # Example of new top line: "AI generated #love #music"
            # You might adjust this depending on how 'summary' is formatted.
            new_content = f"AI Suggestions {summary}\n\n{content}"

            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8', errors='replace') as file:
                file.write(new_content)

            file_count += 1
            updated_files.append(file_path)
            print(f"Updated file ({file_count}): {file_path}")

print("Process completed. Modified files have new AI-generated hashtags at the top.")
print(f"Total files updated: {file_count}")
if updated_files:
    print("List of updated files:")
    for f in updated_files:
        print(f" - {f}")