# agents/aggregator.py


from prompt_ollama_hashtag_aggregator import HashtagAggregator

class AggregatorAgent:
    """
    Combines hashtags from the note content (plain text) and from link analysis,
    then removes duplicates and returns a unified list.
    """
    def __init__(self, ollama_client , model_name):
        self.ollama_agent = ollama_client
        self.aggregator = HashtagAggregator(ollama_client, model_name)


    def run(self, note_hashtags: list, link_hashtags: list) -> list:
        
        combined = set(note_hashtags + link_hashtags)
        combined_hashtags = self.aggregator.combine_hashtags(combined)
        

        # Could add advanced logic here (e.g., ranking or filtering).
        return combined_hashtags