

from prompt_ollama_hashtag_generator import HashtagGenerator


class HashtagGeneratorAgent:
    """Analyzes the note content via Ollama to generate contextually relevant hashtags."""

    def __init__(self, ollama_client, model_name):
        self.ollama_url = ollama_client
        self._hashtag_generator = HashtagGenerator(ollama_client, model_name)


    def _call_ollama(self, content: str) -> list:
        """
        Calls Ollama's API with a prompt and returns a list of generated hashtags.
        Adapt this to your actual prompt engineering / model usage.
        """
        
        link_hashes = self._hashtag_generator.generate_hashtags(content)

        return link_hashes

    def run(self, content: str) -> list:
        # Prepare a minimal prompt for generating hashtags
        prompt = f"Generate relevant hashtags for the following content:\n\n{content}\n\nHashtags:"
        hashtags = self._call_ollama(content)
        return hashtags