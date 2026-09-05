from collections import deque

from crawler import DEFAULT_START_URL, WebCrawler


class SyncWebCrawler(WebCrawler):
    def crawl(self, start_url: str) -> list[str]:
        start_url = self.canonicalize(start_url)
        start_host = self.hostname(start_url)
        seen_urls = {start_url}
        queue = deque([start_url])

        while queue:
            url = queue.popleft()
            links, fetch_dt = self.fetch_links(url)

            for next_url in links:
                page = self.canonicalize(next_url)
                if page in seen_urls or not self.is_same_host(page, start_host):
                    continue
                seen_urls.add(page)
                queue.append(page)

            self.metrics.record_fetch(
                url, fetch_dt, queue=len(queue), discovered=len(seen_urls)
            )

        self.metrics.print_summary(len(seen_urls))
        return list(seen_urls)


if __name__ == "__main__":
    print(SyncWebCrawler().crawl(DEFAULT_START_URL))
