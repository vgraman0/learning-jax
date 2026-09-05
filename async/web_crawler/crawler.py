from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from urllib.parse import urldefrag, urlparse

from utils import get_html, links_from_html

DEFAULT_START_URL = "https://quotes.toscrape.com"


class CrawlMetrics:
    """Wall-clock and per-fetch timings. Safe to call from multiple threads."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._started = time.perf_counter()
        self.pages_fetched = 0
        self.fetch_secs = 0.0

    def elapsed(self) -> float:
        return time.perf_counter() - self._started

    def record_fetch(self, url: str, fetch_dt: float, *, queue: int, discovered: int) -> None:
        with self._lock:
            self.pages_fetched += 1
            self.fetch_secs += fetch_dt
            print(
                f"  [{self.pages_fetched}] fetch={fetch_dt:.2f}s  "
                f"t={self.elapsed():.2f}s  "
                f"queue={queue}  discovered={discovered}  {url}"
            )

    def print_summary(self, discovered: int) -> None:
        elapsed = self.elapsed()
        rate = self.pages_fetched / elapsed if elapsed else 0.0
        print(
            f"pages={self.pages_fetched}  discovered={discovered}  "
            f"wall={elapsed:.2f}s  fetch={self.fetch_secs:.2f}s  "
            f"{rate:.1f} pages/s"
        )


class WebCrawler(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.metrics = CrawlMetrics()

    @staticmethod
    def canonicalize(url: str) -> str:
        return urldefrag(url).url

    @staticmethod
    def hostname(url: str) -> str | None:
        return urlparse(url).hostname

    @staticmethod
    def fetch_links(url: str) -> tuple[list[str], float]:
        started = time.perf_counter()
        html = get_html(url)
        links = links_from_html(html, url) if html is not None else []
        return links, time.perf_counter() - started

    @staticmethod
    def is_same_host(url: str, host: str | None) -> bool:
        return urlparse(url).hostname == host

    @abstractmethod
    def crawl(self, start_url: str) -> list[str]:
        ...


class ConcurrentCrawler(ABC):
    """Shared worker-count setup for multithreaded and async crawlers.

    Put this *before* WebCrawler in the subclass list so ``num_workers``
    reaches this ``__init__`` and ``super()`` still runs WebCrawler's.
    """

    def __init__(self, num_workers: int = 8) -> None:
        super().__init__()
        if num_workers < 1:
            raise ValueError("num_workers must be >= 1")
        self._num_workers = num_workers
