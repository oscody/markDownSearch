
import re

class NotePreprocessorAgent:
    """Cleans up text and identifies if a note contains any links."""

    def _sanitize_url(self, url: str, invalid_chars: str) -> str:
        """Remove invalid characters from a URL."""
        # Remove any invalid characters from the URL
        sanitized_url = re.sub(f"[{re.escape(invalid_chars)}]", "", url)
        return sanitized_url

    def run(self, note: str) -> dict:
        # 1. Clean text (remove unnecessary characters, trim spaces, etc.)
        cleaned_note = note.strip()

        # 2. Check for links using a simple regex pattern
        url_pattern = r'(https?://[^\s]+)'
        links = re.findall(url_pattern, cleaned_note)

        # 3. Sanitize links (remove invalid characters)
        invalid_chars = '><{}|\\^~[]`'
        sanitized_links = [self._sanitize_url(link, invalid_chars) for link in links]

        return {
            "original_note": note,
            "cleaned_note": cleaned_note,
            "links": sanitized_links
        }
    