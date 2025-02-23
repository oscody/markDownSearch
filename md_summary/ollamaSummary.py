import os
import tiktoken
import ollama

# Define the input directory containing text files
input_dir = '/Users/bogle/Dev/gitcode/chatgpt-markdown/outputv2'

# Define the output Markdown file path
output_md_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "summary_ollama.md")

# Specify the AI model to use
model_name = "llama3.2"

ollama_client = ollama.Client()

MAX_CONTEXT_LENGTH = 2048
DESIRED_COMPLETION_TOKENS = 150

# Function to count tokens using tiktoken
def count_tokens(text, model="cl100k_base"):
    encoding = tiktoken.get_encoding(model)
    return len(encoding.encode(text))

prompt_template = """Please analyze the following text and adhere strictly to the instructions:

1. Summary: Provide a concise summary (1–2 sentences) with no more than 20 words, capturing the main idea.
2. Hashtags: Provide 2–3 relevant, topic-related hashtags.

Ensure the summary is brief, professional, and neutral.

Text to analyze:
{}
"""

# Initialize the output Markdown file with headers
with open(output_md_file, 'w') as md_file:
    md_file.write("# Summaries\n\n")
    md_file.write("| Filename | Summary |\n\n")
    

# Process each file in the input directory
for i, filename in enumerate(os.listdir(input_dir)):
    if i >= 3:  # Process only the first 3 files
        break
    file_path = os.path.join(input_dir, filename)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()

        # Construct the initial prompt
        prompt = prompt_template.format(content)

        # Count tokens in the prompt
        prompt_tokens = count_tokens(prompt)

        # Truncate content if the combined token count exceeds the maximum context length
        while prompt_tokens + DESIRED_COMPLETION_TOKENS > MAX_CONTEXT_LENGTH:
            truncate_length = int(len(content) * 0.9)
            content = content[:truncate_length]
            prompt = prompt_template.format(content)
            prompt_tokens = count_tokens(prompt)

        # Prepare the messages with role specification
        messages = [
            {"role": "system", "content": "You are a helpful and concise assistant. You must summarize the given text in 1–2 sentences not exceeding 20 words, and then provide 2–3 relevant hashtags."},
            {"role": "user", "content": prompt}
        ]

        # Send the request to the ollama model with specified parameters
        response = ollama_client.chat(
            model=model_name,
            messages=messages,
            options={
                "temperature": 0.2,
                "top_p": 0.5
            }
        )

        # Extract the summary from the response
        summary = response['message']['content'].strip()

        # Append the filename and summary to the Markdown file
        with open(output_md_file, 'a') as md_file:
            md_file.write(f"| {filename} | {summary} |\n\n")

print(f"Summaries saved to {output_md_file}")