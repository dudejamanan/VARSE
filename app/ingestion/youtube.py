import re
from urllib.parse import urlparse, parse_qs

def extract_video_id(url: str) -> str:
    """
    Extracts the YouTube video ID from different types of YouTube URLs.
    Returns None if no valid ID is found.
    """

    # Case 1: Standard URL (youtube.com/watch?v=...)
    parsed_url = urlparse(url)
    
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        query_params = parse_qs(parsed_url.query)
        if "v" in query_params:
            return query_params["v"][0]

    # Case 2: Short URL (youtu.be/...)
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")

    # Case 3: Embedded URL (/embed/...)
    match = re.search(r"(?:embed\/|v\/|shorts\/)([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)

    return None