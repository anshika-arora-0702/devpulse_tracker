from urllib.parse import urlparse
from exceptions.url_exceptions import InvalidHttpsUrl
  
def _validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise InvalidHttpsUrl(url)
    return url.rstrip("/")
