from tool_web_scrapper import WebpageScrapperTool
from prompt_ollama_hashtag_generator import HashtagGenerator
from tool_web_scrapperB import SeleniumScraper
from tool_youtube_video_scrapper import YoutubeVideoScrapperTool

class LinkContentAnalyzerAgent:
    """
    Retrieves basic metadata (e.g., title, description) from each link,
    then optionally calls Ollama to generate additional hashtags from that metadata.
    """

    def __init__(self, ollama_client , model_name):
        self.ollama_agent = ollama_client
        self.web_scrapper_tool = WebpageScrapperTool()
        self._hashtag_generator = HashtagGenerator(ollama_client, model_name)
        self.selenium_Scraper = SeleniumScraper()
        self.youtubeVideo_scrapper_tool = YoutubeVideoScrapperTool()

    def _scrape_webpage(self, url: str) -> dict:
        try:
            # Use WebpageScrapperTool to fetch and process webpage content
            # webpage_content = self.selenium_Scraper.run(url)
            webpage_content = self.web_scrapper_tool.execute(url=url)
            if not webpage_content:
                webpage_content = self.selenium_Scraper.run(url)
            return webpage_content
        except Exception as e:
            print(f"Error scraping webpage {url}: {e}")
            return {}

    def run(self, valid_links: list) -> dict:
        link_analysis = []
        link_based_hashtags = []

        for link in valid_links:

            print('LinkContentAnalyzerAgent',link)
            # webpage_content = self._scrape_webpage(link)

            if "youtu.be" in link or "youtube.com" in link:
                webpage_content = self.youtubeVideo_scrapper_tool.execute(link)
            else:
                webpage_content = self._scrape_webpage(link)

                
            # Safely get the text from the scrapped data
            if not webpage_content.strip():
                # If there's no text, skip or store empty data
                link_analysis.append({
                    "url": link,
                    "metadata": webpage_content,
                    "hashtags": []
                })
                continue

            link_hashes = self._hashtag_generator.generate_hashtags(webpage_content)
            link_based_hashtags.extend(link_hashes)

            link_analysis.append({
                "url": link,
                "metadata": webpage_content,
                "hashtags": link_hashes
            })

        return {
            "link_analysis": link_analysis,
            "link_based_hashtags": list(set(link_based_hashtags))  # deduplicate at this stage
        }