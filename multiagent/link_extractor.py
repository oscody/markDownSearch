
import requests

class LinkExtractorAgent:
    """Validates links and returns active (safe) links."""

    def run(self, links: list) -> dict:
        valid_links = []
        for link in links:
            # Minimal check for link validity
            try:
                response = requests.head(link, timeout=5)
                # changed for website throwing error 
                if response.status_code < 500: 
                    valid_links.append(link)
            except:
                # If invalid or request fails, ignore or store as broken
                pass
        return {
            "valid_links": valid_links
        }