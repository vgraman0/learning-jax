import asyncio
import time
from asyncio import FIRST_COMPLETED

import aiohttp

from crawler import ConcurrentCrawler, DEFAULT_START_URL, WebCrawler
from rate_limiter import RateLimiter
from utils import links_from_html


class AsyncWebCrawler(ConcurrentCrawler, WebCrawler):
    def __init__(self, num_workers: int = 8, rps=30, use_uvloop: bool = False) -> None:
        super().__init__(num_workers)
        self._use_uvloop = use_uvloop
        self.limiter = RateLimiter(rps)

    def crawl(self, start_url: str) -> list[str]:
        if self._use_uvloop:
            import uvloop

            return asyncio.run(self._crawl(start_url), loop_factory=uvloop.new_event_loop)
        return asyncio.run(self._crawl(start_url))

    @staticmethod
    async def _fetch_links(session: aiohttp.ClientSession, url: str) -> tuple[list[str], float, float]:
        started = time.perf_counter()
        try:
            async with session.get(url) as response:
                html = await response.text() if response.status == 200 else None
        except (aiohttp.ClientError, TimeoutError, OSError):
            return [], time.perf_counter() - started, 0.0

        links = links_from_html(html, url) if html else []
        # aiohttp yields during I/O, so the event loop is not blocked on the GET.
        return links, time.perf_counter() - started, 0.0

    async def _crawl(self, start_url: str) -> list[str]:
        start_url = self.canonicalize(start_url)
        start_host = self.hostname(start_url)
        seen_urls = {start_url}

        async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=self._num_workers),
                timeout=aiohttp.ClientTimeout(total=10),
                headers={"User-Agent": "web-crawler-interview/0.1"}) as session:
            sem = asyncio.Semaphore(self._num_workers)

            async def bounded_fetch(_url: str):
                async with sem:
                    blocked_dt = await self.limiter.acquire()
                    links, fetch_dt, _ = await self._fetch_links(session, _url)
                    return links, fetch_dt, blocked_dt

            task = asyncio.create_task(bounded_fetch(start_url))
            pending = {task}
            in_flight = {task: start_url}

            while pending:
                done, pending = await asyncio.wait(pending, return_when=FIRST_COMPLETED)
                for completed_task in done:
                    url = in_flight.pop(completed_task)
                    links, fetch_dt, blocked_dt = await completed_task

                    for next_url in links:
                        page = self.canonicalize(next_url)
                        if page in seen_urls or not self.is_same_host(page, start_host):
                            continue
                        seen_urls.add(page)
                        child = asyncio.create_task(bounded_fetch(page))
                        pending.add(child)
                        in_flight[child] = page

                    self.metrics.record_fetch(
                        url, fetch_dt, queue=len(pending), discovered=len(seen_urls),
                        blocked_dt=blocked_dt,
                    )

        self.metrics.print_summary(len(seen_urls))
        return list(seen_urls)


if __name__ == "__main__":
    print(AsyncWebCrawler(num_workers=30).crawl(DEFAULT_START_URL))
