import os
import tiktoken
import ollama
import re

# Define the input directory containing your top-level folders
# input_dir = '/Users/bogle/Dev/gitcode/chatgpt-markdown/outputv2'
input_dir = '/Users/bogle/Dev/obsidian/Bogle'

# Define the allowed top-level directories
allowed_dirs = {"1. Projects", "2. Areas", "3. Resources", "4. Archives"}

# Specify the AI model to use
model_name = "llama3.2"

ollama_client = ollama.Client()

MAX_CONTEXT_LENGTH = 2048
DESIRED_COMPLETION_TOKENS = 150


file_count = 0
file_limit = 50
# file_limit = None  # Set to None to process all files


# Markdown output file
output_file = 'ollamaHashtagsV3.md'

# Initialize the Markdown table structure
markdown_table = "| Filename | AI Suggestions |\n|----------|----------------|\n"

# Function to count tokens using tiktoken
def count_tokens(text, model="cl100k_base"):
    encoding = tiktoken.get_encoding(model)
    return len(encoding.encode(text))



prompt_template = """
Please analyze the following text and strictly adhere to the instructions below:
1. Purpose:
   - Identify exactly 5 hashtags that summarize the content, capture key themes, or optimize for searchability.
   - The hashtags should prioritize niche terms relevant to unique ideas or specialized communities while including trending terms sparingly to maintain visibility.
2. Customization:
   - Compound phrases are allowed to enhance specificity and clarity (e.g., #AtomicNotes).
   - Hashtags should be original and relevant to niche topics. Avoid redundancy (e.g., merging #poem and #poems if both apply).
   - Exclude overly generic terms (e.g., #Notes, #AI) unless paired with specific contexts (e.g., #AINeuralNetworks).
3. Adaptability:
   - The prompt should be flexible enough to handle both structured (e.g., bullet points) and unstructured (e.g., prose) text inputs.
   - Hashtags should adapt to evolving use cases, such as including tags for yearly updates or sentiment-based categorization.
4. Validation:
   - Ensure the hashtags are distinct, non-redundant, and directly tied to the text's content.
   - Generic hashtags should be limited or filtered out in favor of specific, meaningful terms that add organizational value.

5. Output:
   - Output only the 5 hashtags on a single line, separated by a single space.
   - Do not include any additional text, commentary, formatting, line breaks, or punctuation beyond the hashtags.
   - Each hashtag must start with '#' immediately followed by a single continuous word or phrase with no internal spaces (e.g., #ExampleHashtag).

Text to analyze:
{}
"""


# Recursively walk through directories
for root, dirs, files in os.walk(input_dir):
    # # Prune directories so that at the top level we only descend into allowed_dirs
    # if root == input_dir:
    #     dirs[:] = [d for d in dirs if d in allowed_dirs]

    for filename in files:
        # Only process .md files
        if not filename.lower().endswith('.md'):
            continue

        # If a file limit is set and reached, break
        if file_limit is not None and file_count >= file_limit:
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

            # Normalize whitespace: ensure a single line
            summary = ' '.join(summary.split())

            # Replace occurrences of "# " with "#"
            summary = re.sub(r'#\s+', '#', summary)

            # Add a new row to the Markdown table
            markdown_table += f"| {filename} | {summary} |\n"

            file_count += 1
            print(f"Processed file ({file_count}): {file_path}")

# Write the Markdown table to the output file
with open(output_file, 'w', encoding='utf-8') as md_file:
    md_file.write(markdown_table)

print("Markdown table has been created in 'ollamaHashtags.md'.")