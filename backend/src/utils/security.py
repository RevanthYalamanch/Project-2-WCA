import socket
import re
from urllib.parse import urlparse
import bleach

# --- Configuration for Whitelist/Blacklist ---
# These lists can be expanded or moved to a separate settings file.
# By default, the whitelist is empty (allowing all URLs that are not blacklisted).
URL_WHITELIST_PATTERNS = []
# Example: Disallow scraping from any '.gov' or '.mil' domain
URL_BLACKLIST_PATTERNS = [r"^https?://[a-zA-Z0-9-.]+\.gov(/.*)?$", r"^https?://[a-zA-Z0-9-.]+\.mil(/.*)?$"]


# --- Component 1 & 2: URL Validation and Private IP Blocking ---

class URLValidator:
    """
    Handles comprehensive URL validation including whitelists, blacklists, and SSRF prevention.
    """
    def __init__(self, whitelist=URL_WHITELIST_PATTERNS, blacklist=URL_BLACKLIST_PATTERNS):
        self.whitelist = [re.compile(p) for p in whitelist]
        self.blacklist = [re.compile(p) for p in blacklist]

    def is_allowed(self, url: str) -> bool:
        """
        Checks a URL against the configured whitelist and blacklist.
        """
        # If a whitelist is defined, the URL must match one of its patterns.
        if self.whitelist and not any(pattern.match(url) for pattern in self.whitelist):
            print(f"URL blocked: Not in whitelist - {url}")
            return False
        
        # The URL must not match any pattern in the blacklist.
        if self.blacklist and any(pattern.match(url) for pattern in self.blacklist):
            print(f"URL blocked: In blacklist - {url}")
            return False
        
        return True

    def _is_private_ip(self, ip: str) -> bool:
        """Checks if the given IP address is in a private range."""
        try:
            is_private = socket.inet_aton(ip)
            return (
                is_private[0] == 10 or
                (is_private[0] == 172 and 16 <= is_private[1] <= 31) or
                (is_private[0] == 192 and is_private[1] == 168) or
                is_private[0] == 127
            )
        except socket.error:
            return False

    def prevent_ssrf(self, url: str) -> bool:
        """
        Validates a URL to prevent SSRF by checking for private IP ranges.
        Returns True if the URL is safe, False otherwise.
        """
        try:
            hostname = urlparse(url).hostname
            if not hostname:
                return False
            
            ip_address = socket.gethostbyname(hostname)

            if self._is_private_ip(ip_address):
                print(f"URL blocked: Points to a private IP - {ip_address}")
                return False

            return True
        except (socket.gaierror, ValueError):
            return False

# --- Component 3 & 4: Content Length and File Type Validation ---

def validate_content_headers(headers: dict) -> bool:
    """
    Validates response headers for content type and length.
    """
    # File Type Validation
    content_type = headers.get('Content-Type', '')
    if 'text/html' not in content_type:
        raise ValueError(f"Invalid content type: {content_type}. Only 'text/html' is allowed.")

    # Content Length Restriction
    content_length = int(headers.get('Content-Length', 0))
    max_size = 5 * 1024 * 1024  # 5 MB
    if content_length > 0 and content_length > max_size:
        raise ValueError(f"Content length {content_length} exceeds the max size of {max_size} bytes.")
    
    return True

# --- Component 5: XSS Prevention in Scraped Content ---

def sanitize_html_content(dirty_html: str) -> str:
    """
    Cleans HTML content to prevent Cross-Site Scripting (XSS) attacks.
    It strips dangerous tags (like <script>) and attributes, leaving only safe HTML.
    """
    # Define a set of allowed, safe HTML tags and attributes
    allowed_tags = {'p', 'br', 'b', 'i', 'em', 'strong', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'a', 'span', 'div'}
    allowed_attrs = {'href': ['http', 'https'], 'title': True}
    
    # Clean the HTML
    clean_html = bleach.clean(
        dirty_html,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True  # Removes disallowed tags entirely instead of escaping them
    )
    return clean_html