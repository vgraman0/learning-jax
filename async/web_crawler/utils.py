from __future__ import annotations

from html.parser import HTMLParser
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

_TIMEOUT_SEC = 10
_HEADERS = {"User-Agent": "web-crawler-interview/0.1"}


def get_html(url: str) -> str | None:
    """Blocking fetch with urlopen. Returns HTML, or None on timeout / 4xx/5xx / network error."""
    request = Request(url, headers=_HEADERS)
    try:
        with urlopen(request, timeout=_TIMEOUT_SEC) as response:
            if response.status != 200:
                return None
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except (URLError, TimeoutError, ValueError, OSError):
        return None


class _HrefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for name, value in attrs:
            if name == "href" and value:
                self.hrefs.append(value.strip())


def links_from_html(html: str, base_url: str) -> list[str]:
    """Return absolute http(s) links from <a href>, resolved against base_url. No fetch."""
    parser = _HrefParser()
    parser.feed(html)
    parser.close()

    urls: list[str] = []
    for href in parser.hrefs:
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
            continue
        absolute = urljoin(base_url, href)
        if absolute.startswith(("http://", "https://")):
            urls.append(absolute)
    return urls
