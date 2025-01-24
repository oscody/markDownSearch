# prompt_ollama_hashtag_generator

import tiktoken

PROMPT_TEMPLATE = """Please analyze the following text and strictly follow these instructions:
1. Purpose:
- Identify exactly 5 hashtags that summarize the content, capture key themes, or optimize for searchability.
2. Output:
- Output only the 5 hashtags on a single line, separated by a single space.
- Do not include any additional text, commentary, formatting, line breaks, or punctuation beyond the hashtags.
- Each hashtag must start with '#' immediately followed by a single continuous word or phrase with no internal spaces (e.g., #ExampleHashtag).
- If unable to generate 5 hashtags, output only "#unabletoGenerate".
3. 
Text to analyze:
{}
"""

class HashtagGenerator:
    def __init__(self, ollama_client, model_name, max_context_length=2048, desired_completion_tokens=150):
        self.ollama_client = ollama_client
        self.model_name = model_name
        self.MAX_CONTEXT_LENGTH = max_context_length
        self.DESIRED_COMPLETION_TOKENS = desired_completion_tokens

    def _count_tokens(self, text: str, model="cl100k_base"):
        encoding = tiktoken.get_encoding(model)
        return len(encoding.encode(text))
    
    def _remove_single_hash_tags(self, hashtags: list[str]) -> list[str]:
        """
        Removes any entries that are literally just '#'.
        """
        filtered = [h for h in hashtags if h.strip() != "#"]
        return filtered

    def _remove_i_cant_tags(self, hashtags: list[str]) -> list[str]:
        """
        Removes any entries that contain "I can't".
        """
        filtered = [h for h in hashtags if "I can't" not in h]
        return filtered

    def generate_hashtags(self, content: str) -> list:
        """
        Generates up to 2 hashtags based on the given content
        using an Ollama model with the specified prompt template.
        """

        prompt = PROMPT_TEMPLATE.format(content)
        prompt_tokens = self._count_tokens(prompt)

        # Truncate content if needed to stay within token limit
        while (prompt_tokens + self.DESIRED_COMPLETION_TOKENS) > self.MAX_CONTEXT_LENGTH:
            truncate_length = int(len(content) * 0.9)
            content = content[:truncate_length]
            prompt = PROMPT_TEMPLATE.format(content)
            prompt_tokens = self._count_tokens(prompt)

        messages = [
            {
                "role": "system",
                "content": "You are a reliable, concise, and compliant assistant who follows instructions exactly."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Call Ollama
        response = self.ollama_client.chat(
            model=self.model_name,
            messages=messages,
            options={
                "temperature": 0.2,
                "top_p": 0.5
            }
        )

        # Extract and normalize the hashtags from Ollama's response
        raw_output = response['message']['content'].strip()
        normalized_output = ' '.join(raw_output.split())
        candidate_tags = [tag for tag in normalized_output.split() if tag.startswith('#')]
        
        # Post-process with the two separate filters
        candidate_tags = self._remove_single_hash_tags(candidate_tags)
        candidate_tags = self._remove_i_cant_tags(candidate_tags)
        print('HashtagGenerator',candidate_tags)
        return candidate_tags