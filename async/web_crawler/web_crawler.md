# Web Crawler

Two related interview problems. Start with the BFS phone-screen version; the onsite version layers concurrency, politeness, and distributed design on top.

| Problem | Tags | Frequency |
|---|---|---|
| **Async Web Crawler** | `#bfs` `#coding` `#phone` | Common, 6/10 |
| **Web Crawler** | `#coding` `#onsite` `#phone` | Popular, 10/10 |

---

## Problem

Given a start URL, crawl every page reachable from it by following links, staying on the same host.

You are given these helpers (do not implement them):

```
get_html(url: str) -> str | None
    Fetch the page with a blocking HTTP GET. Returns HTML, or None on
    failure (timeout, 4xx/5xx, network error).

links_from_html(html: str, base_url: str) -> list[str]
    Return absolute URLs found in the HTML. Relative links are already
    resolved against base_url. Does not fetch.
```

Implement:

```
def crawl(start_url: str) -> list[str]
```

---

## Requirements

1. **Same host only.** Do not follow links to a different hostname than `start_url`. `http://news.example.com` is not `http://example.com`.
2. **Each URL is fetched at most once.**
3. **BFS traversal.** Visit pages in breadth-first order.
4. **Fragments are not distinct pages.** `http://example.com/a` and `http://example.com/a#section` are the same URL.
5. **The link graph may contain cycles.**
6. **Failed fetches must not crash the crawler.** Skip that URL and continue.
7. **Return the list of discovered URLs on the start host** (including `start_url`). Order may follow BFS, but uniqueness matters more than a specific permutation.

---

## Example

```
start_url = "http://example.com/home"

http://example.com/home  links to  /about, /blog, https://other.com/x
http://example.com/about links to  /home, /team
http://example.com/blog  links to  /about
http://example.com/team  links to  /home
https://other.com/x      links to  /y          (different host)

crawl("http://example.com/home")
    -> ["http://example.com/home",
        "http://example.com/about",
        "http://example.com/blog",
        "http://example.com/team"]
```

---

## Clarifying questions worth asking

- Same *host* or same *registrable domain*?
- Normalize trailing slashes, default ports, `http` vs `https`, query strings, host case?
- Max pages / max depth, or unbounded until the frontier is empty?
- Return URLs only, or `url -> html`?
- Is `get_html` allowed to be called concurrently, or is it single-threaded by default?

---

## Follow-ups

### 1 — Multi-threaded crawler

`get_html` is I/O-bound and slow. Parallelize `crawl` so several pages are in flight at once.

- Bound the number of concurrent fetches.
- The visited set and the work queue are shared across workers.
- Still fetch each URL at most once.
- The process must exit when there is no remaining work *and* no worker is still fetching.

Discuss threads vs processes for this workload, how you avoid double-fetch races, and how you detect termination without deadlock.

### 2 — Async crawler

Rewrite the same crawler with `asyncio` and an async HTTP client (e.g. `aiohttp`). Same correctness bar as Follow-up 1: unique visits, same-host restriction, bounded concurrency, clean shutdown.

### 3 — robots.txt and rate limiting

Make the crawler something you could point at a real site.

**robots.txt**

- Honor Allow / Disallow for your user-agent.
- Cache the parsed file per host.
- Define behavior if `robots.txt` is missing or the fetch fails.

**Rate limiting**

- Cap request rate *per host* (N/sec, or a minimum gap between requests to the same origin).
- Extra workers must not stampede one host.

If time remains: User-Agent, timeouts, backoff on 429/503, Crawl-Delay, a max-page or max-depth cap.

### 4 — Distributed crawl (design only)

The corpus no longer fits on one machine. Sketch a multi-worker system. You are not expected to code this in the session.

- Where does the frontier live?
- How do you dedup a visited set larger than one process's memory?
- Partition by host or by URL? What breaks if you hash by URL when `robots.txt` and per-host rate limits are in play?
- Worker crash, at-least-once delivery, duplicate fetches.
- A few huge hosts vs many small ones.
- Recrawl / freshness / priority.

---

Measured wall / fetch / blocked times for the three implementations: [crawler_comparison.md](crawler_comparison.md).
