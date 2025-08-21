import requests
import random
import time
from ..utils.security import URLValidator
from ..processors.content_extractor import extract_and_clean_content

class WebScraperService:
    def __init__(self):
        self.session = requests.Session()
        self.validator = URLValidator()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        ]
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })

    def _validate_url(self, url: str) -> bool:
        return self.validator.is_allowed(url) and self.validator.prevent_ssrf(url)

    async def scrape_url(self, url: str) -> dict: # Returns a dictionary now
        if not self._validate_url(url):
            raise ValueError("URL is invalid, blacklisted, or points to a restricted address.")

        headers = self.session.headers.copy()
        headers['User-Agent'] = random.choice(self.user_agents)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                time.sleep(1)
                with self.session.get(url, headers=headers, timeout=15, stream=True) as response:
                    response.raise_for_status()

                    content_type = response.headers.get('Content-Type', '')
                    if 'text/html' not in content_type:
                        raise ValueError(f"URL does not point to an HTML document. Content-Type: {content_type}")

                    content = response.content
                    html_content = content.decode('utf-8', errors='ignore')
                    
                    # Directly return the full dictionary from the processor
                    return extract_and_clean_content(html_content)

            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt + 1 == max_retries:
                    raise ConnectionError(f"Failed to fetch URL after {max_retries} attempts.")
                time.sleep(2)

        raise ConnectionError("Failed to fetch URL after all retries.")