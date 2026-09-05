from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

from crawler import ConcurrentCrawler, DEFAULT_START_URL, WebCrawler


class MultithreadedWebCrawler(ConcurrentCrawler, WebCrawler):
    def crawl(self, start_url: str) -> list[str]:
        start_url = self.canonicalize(start_url)
        start_host = self.hostname(start_url)
        seen_urls = {start_url}

        with ThreadPoolExecutor(max_workers=self._num_workers) as pool:
            future = pool.submit(self.fetch_links, start_url)
            pending = {future}
            in_flight = {future: start_url}

            while pending:
                done, pending = wait(pending, return_when=FIRST_COMPLETED)
                for fut in done:
                    url = in_flight.pop(fut)
                    links, fetch_dt, blocked_dt = fut.result()

                    for next_url in links:
                        page = self.canonicalize(next_url)
                        if page in seen_urls or not self.is_same_host(page, start_host):
                            continue
                        seen_urls.add(page)
                        child = pool.submit(self.fetch_links, page)
                        pending.add(child)
                        in_flight[child] = page

                    self.metrics.record_fetch(
                        url, fetch_dt, queue=len(pending), discovered=len(seen_urls),
                        blocked_dt=blocked_dt,
                    )

        self.metrics.print_summary(len(seen_urls))
        return list(seen_urls)


if __name__ == "__main__":
    print(MultithreadedWebCrawler(num_workers=100).crawl(DEFAULT_START_URL))
