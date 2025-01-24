import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from newspaper import Article

class WebpageScrapperTool:
    def execute(self, url="", **kwargs):
        if not url:
            print("No URL provided.")
            return

        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                print("Invalid URL format.")
                return
            
            # Fetch webpage content
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Use newspaper3k for article extraction
            article = Article(url)
            article.download()
            article.parse()

            # If it's not an article, fall back to BeautifulSoup
            if not article.text:
                soup = BeautifulSoup(response.content, 'html.parser')
                text_content = ' '.join(soup.stripped_strings)
            else:
                text_content = article.text

            print('scrapper',text_content)
            return text_content

        except requests.RequestException as e:
            print(f"Error fetching webpage: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")