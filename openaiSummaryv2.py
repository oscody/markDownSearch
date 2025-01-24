import os
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken

load_dotenv()

input_dir = '/Users/bogle/Dev/gitcode/chatgpt-markdown/outputv2'
script_dir = os.path.dirname(os.path.abspath(__file__))
output_md_file = os.path.join(script_dir, "summary.md")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_CONTEXT_LENGTH = 4097
# We'll set a desired completion length
DESIRED_COMPLETION_TOKENS = 150

# Use tiktoken to accurately count tokens
def count_tokens(text, model="gpt-3.5-turbo-instruct"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

prompt_template = """Please read the following text and produce a concise summary (1–2 sentences) that captures its main idea. 
After the summary, provide a short list of relevant, topic-related hashtags (e.g., #Keyword, #Topic). 
Maintain a professional and neutral tone throughout:

{}
"""
with open(output_md_file, 'w') as md_file:
    md_file.write("# Summaries\n\n")
    md_file.write("| Filename | Summary |\n")
    md_file.write("|----------|---------|\n")

for i, filename in enumerate(os.listdir(input_dir)):
    if i >= 3:  # only process first 3 files
        break
    file_path = os.path.join(input_dir, filename)
    print(f"file_path  {file_path}")
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()

        # Construct initial prompt
        prompt = prompt_template.format(content)
        
        # Count tokens
        prompt_tokens = count_tokens(prompt)

        # If prompt + completion is too large, truncate
        # We need prompt_tokens + DESIRED_COMPLETION_TOKENS <= MAX_CONTEXT_LENGTH
        while prompt_tokens + DESIRED_COMPLETION_TOKENS > MAX_CONTEXT_LENGTH:
            # Truncate content further. For example, remove last 10% of text
            truncate_length = int(len(content) * 0.9)
            content = content[:truncate_length]
            prompt = prompt_template.format(content)
            prompt_tokens = count_tokens(prompt)
        
        # Now send request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt_template},
                {"role": "user", "content": prompt}
            ]
        )

        summary = response.choices[0].message.content

        with open(output_md_file, 'a') as md_file:
            md_file.write(f"| {filename} | {summary} |\n")

print(f"Summaries saved to {output_md_file}")