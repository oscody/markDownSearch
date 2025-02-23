import os
import re
import tiktoken
import ollama
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# 1. Configuration
input_dir = '/Users/bogle/Dev/obsidian/Bogle'
allowed_dirs = {"1. Projects", "2. Areas", "3. Resources", "4. Archives"}
model_name = "llama3.2"
ollama_client = ollama.Client()

MAX_CONTEXT_LENGTH = 2048
DESIRED_COMPLETION_TOKENS = 150
file_count = 0
file_limit = 50  # or None for no limit
output_file = 'ollamaHashtagsV4.md'

# 2. Prompt template
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

Similar/Related Document Hashtags for reference:
{similar_hashtags}

Text to analyze:
{content}
"""

# 3. Token counting function
def count_tokens(text, model="cl100k_base"):
    encoding = tiktoken.get_encoding(model)
    return len(encoding.encode(text))

# 4. Embedding Model Initialization (using Sentence-Transformers)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text: str) -> np.ndarray:
    """Return the embedding vector (float32) for a piece of text."""
    vector = embedding_model.encode([text], convert_to_numpy=True)
    return vector.astype('float32')

# 5. FAISS Index Setup
#    We'll keep an in-memory index, plus a list to store metadata
faiss_index = None
stored_metadata = []  # will store tuples of (filename, hashtags, embedding_vector)

def initialize_faiss_index(dimension: int):
    """Create a new FAISS index with L2 distance."""
    return faiss.IndexFlatL2(dimension)

def add_to_index(filename: str, hashtags: str, embedding: np.ndarray):
    """Add a new embedding to the FAISS index and store its metadata."""
    global faiss_index, stored_metadata

    # If the index is not initialized yet, do so
    if faiss_index is None:
        dimension = embedding.shape[1]  # number of dimensions from the embedding
        faiss_index = initialize_faiss_index(dimension)

    # Add to FAISS
    faiss_index.add(embedding)
    # Keep track of metadata
    stored_metadata.append((filename, hashtags, embedding))

def search_similar(embedding: np.ndarray, top_k=3):
    """Search FAISS index for top_k similar embeddings."""
    global faiss_index, stored_metadata

    if faiss_index is None or len(stored_metadata) == 0:
        # No data in index yet
        return []

    # Perform search
    distances, indices = faiss_index.search(embedding, top_k)
    # Flatten results (since we pass batch size=1)
    idx_list = indices[0]
    results = []
    for i in idx_list:
        if i < len(stored_metadata):
            filename, hashtags, stored_vector = stored_metadata[i]
            results.append((filename, hashtags))
    return results

# 6. Markdown table header
markdown_table = "| Filename | AI Suggestions |\n|----------|----------------|\n"

# 7. Main loop: Recursively walk through directories
for root, dirs, files in os.walk(input_dir):
    # (Optional) If you only want to descend into certain top-level dirs:
    # if root == input_dir:
    #     dirs[:] = [d for d in dirs if d in allowed_dirs]

    for filename in files:
        if not filename.lower().endswith('.md'):
            continue

        # If a file limit is set and reached, break
        if file_limit is not None and file_count >= file_limit:
            break

        file_path = os.path.join(root, filename)

        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()

            # -- Step A: Embed the current file's text
            current_embedding = embed_text(content)

            # -- Step B: Retrieve similar documents and gather their hashtags
            similar_docs = search_similar(current_embedding, top_k=3)
            similar_hashtags_list = [doc[1] for doc in similar_docs if doc[1]]
            # Flatten or join them. You might refine how you pass them into the prompt.
            # For simplicity, we just concatenate them in a single string:
            combined_hashtags = " ".join(similar_hashtags_list) or "None"

            # -- Step C: Build the prompt with reference to similar hashtags
            prompt = prompt_template.format(
                similar_hashtags=combined_hashtags,
                content=content
            )

            # Count tokens and possibly truncate content if needed
            prompt_tokens = count_tokens(prompt)
            truncated_content = content

            while prompt_tokens + DESIRED_COMPLETION_TOKENS > MAX_CONTEXT_LENGTH:
                # Truncate content
                truncate_length = int(len(truncated_content) * 0.9)
                truncated_content = truncated_content[:truncate_length]
                prompt = prompt_template.format(
                    similar_hashtags=combined_hashtags,
                    content=truncated_content
                )
                prompt_tokens = count_tokens(prompt)

            messages = [
                {
                    "role": "system", 
                    "content": "You are a reliable, concise, and compliant assistant who follows the user's instructions and policies."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            # -- Step D: Get LLM-generated hashtags
            response = ollama_client.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": 0.2,
                    "top_p": 0.5
                }
            )

            # The LLM returns a response dict; extract the 'message' content
            summary = response['message']['content'].strip()
            # Normalize whitespace
            summary = ' '.join(summary.split())
            # Fix patterns like "# " => "#"
            summary = re.sub(r'#\s+', '#', summary)

            # -- Step E: Update the FAISS index with the new file embedding & hashtags
            add_to_index(filename, summary, current_embedding)

            # -- Step F: Add a row to the Markdown table
            markdown_table += f"| {filename} | {summary} |\n"
            file_count += 1
            print(f"Processed file ({file_count}): {file_path}")

# 8. Write the Markdown table to the output file
with open(output_file, 'w', encoding='utf-8') as md_file:
    md_file.write(markdown_table)

print(f"Markdown table has been created in '{output_file}'.")