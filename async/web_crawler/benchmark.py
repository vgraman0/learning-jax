"""Compare sync, multithreaded, and async crawlers across worker counts."""

from __future__ import annotations

import json
from pathlib import Path

from async_web_crawler import AsyncWebCrawler
from crawler import DEFAULT_START_URL, WebCrawler
from multithreaded_web_crawler import MultithreadedWebCrawler
from sync_web_crawler import SyncWebCrawler

WORKER_COUNTS = (1, 2, 4, 8, 16, 32, 64, 128, 256)
RESULTS_PATH = Path(__file__).with_name("crawler_comparison.json")
PLOT_PATH = Path(__file__).with_name("crawler_comparison.svg")
MARKDOWN_PATH = Path(__file__).with_name("crawler_comparison.md")


def _stats(crawler: WebCrawler, urls: list[str]) -> dict[str, float | int]:
    wall = crawler.metrics.elapsed()
    pages = crawler.metrics.pages_fetched
    return {
        "pages": pages,
        "discovered": len(urls),
        "wall": wall,
        "fetch": crawler.metrics.fetch_secs,
        "blocked": crawler.metrics.blocked_secs,
        "pages_per_s": pages / wall if wall else 0.0,
        "avg_blocked_workers": crawler.metrics.blocked_secs / wall if wall else 0.0,
    }


def run_crawler(crawler: WebCrawler, start_url: str) -> dict[str, float | int]:
    crawler.metrics.verbose = False
    urls = crawler.crawl(start_url)
    return _stats(crawler, urls)


def _fmt_run(stats: dict) -> str:
    return (
        f"  pages={stats['pages']}  discovered={stats['discovered']}  "
        f"wall={stats['wall']:.2f}s  fetch={stats['fetch']:.2f}s  "
        f"blocked={stats['blocked']:.2f}s  {stats['pages_per_s']:.1f} pages/s"
    )


def _crawler_factories() -> tuple[tuple[str, object], ...]:
    return (
        ("multithreaded", MultithreadedWebCrawler),
        ("async", AsyncWebCrawler),
        ("async_uvloop", lambda num_workers: AsyncWebCrawler(num_workers, use_uvloop=True)),
    )


def main() -> None:
    start_url = DEFAULT_START_URL
    if RESULTS_PATH.exists():
        results = json.loads(RESULTS_PATH.read_text())
        results["workers"] = list(WORKER_COUNTS)
        print(f"loaded {RESULTS_PATH}")
    else:
        results = {"start_url": start_url, "workers": list(WORKER_COUNTS)}

    if "sync" not in results:
        print("sync baseline")
        sync = run_crawler(SyncWebCrawler(), start_url)
        results["sync"] = sync
        print(_fmt_run(sync))
    else:
        print("skipping sync (already in results)")

    for name, factory in _crawler_factories():
        if name in results:
            print(f"skipping {name} (already in results)")
            continue
        runs = []
        for n in WORKER_COUNTS:
            print(f"{name} workers={n}")
            stats = run_crawler(factory(num_workers=n), start_url)
            stats["num_workers"] = n
            runs.append(stats)
            print(_fmt_run(stats))
        results[name] = runs

    RESULTS_PATH.write_text(json.dumps(results, indent=2) + "\n")
    print(f"wrote {RESULTS_PATH}")
    plot(results)
    print(f"wrote {PLOT_PATH}")
    write_markdown(results)
    print(f"wrote {MARKDOWN_PATH}")


def plot(results: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    workers = results["workers"]
    sync = results["sync"]
    mt_wall = [r["wall"] for r in results["multithreaded"]]
    mt_fetch = [r["fetch"] for r in results["multithreaded"]]
    mt_blocked = [r["blocked"] for r in results["multithreaded"]]
    async_wall = [r["wall"] for r in results["async"]]
    async_fetch = [r["fetch"] for r in results["async"]]
    async_blocked = [r["blocked"] for r in results["async"]]
    uv_wall = [r["wall"] for r in results["async_uvloop"]]
    uv_fetch = [r["fetch"] for r in results["async_uvloop"]]
    uv_blocked = [r["blocked"] for r in results["async_uvloop"]]

    fig, (ax_time, ax_blocked) = plt.subplots(
        2, 1, sharex=True, figsize=(10, 8.5), height_ratios=[1.15, 1]
    )

    ax_time.axhline(sync["wall"], color="#4c4c4c", linestyle="--", linewidth=1.4, label="sync wall")
    ax_time.axhline(sync["fetch"], color="#9a9a9a", linestyle=":", linewidth=1.4, label="sync fetch")
    ax_time.plot(workers, mt_wall, "o-", color="#1f77b4", label="multithreaded wall")
    ax_time.plot(workers, mt_fetch, "o--", color="#1f77b4", alpha=0.55, label="multithreaded fetch")
    ax_time.plot(workers, async_wall, "s-", color="#d62728", label="async wall")
    ax_time.plot(workers, async_fetch, "s--", color="#d62728", alpha=0.55, label="async fetch")
    ax_time.plot(workers, uv_wall, "^-", color="#2ca02c", label="async+uvloop wall")
    ax_time.plot(workers, uv_fetch, "^--", color="#2ca02c", alpha=0.55, label="async+uvloop fetch")
    ax_time.set_ylabel("seconds")
    ax_time.set_title(f"Crawler wall vs fetch time\n{results['start_url']}")
    ax_time.grid(True, which="both", linestyle=":", alpha=0.5)
    ax_time.legend(loc="upper right", fontsize=8)

    ax_blocked.axhline(
        sync["blocked"], color="#4c4c4c", linestyle="--", linewidth=1.4, label="sync blocked"
    )
    ax_blocked.plot(workers, mt_blocked, "o-", color="#1f77b4", label="multithreaded blocked")
    ax_blocked.plot(workers, async_blocked, "s-", color="#d62728", label="async blocked")
    ax_blocked.plot(workers, uv_blocked, "^-", color="#2ca02c", label="async+uvloop blocked")
    ax_blocked.set_xscale("log", base=2)
    ax_blocked.set_xticks(workers)
    ax_blocked.set_xticklabels([str(n) for n in workers])
    ax_blocked.set_xlabel("num_workers")
    ax_blocked.set_ylabel("blocked thread-seconds")
    ax_blocked.set_title("Time stuck in blocking get_html / urlopen")
    ax_blocked.grid(True, which="both", linestyle=":", alpha=0.5)
    ax_blocked.legend(loc="upper right", fontsize=8)

    fig.tight_layout()
    fig.savefig(PLOT_PATH)
    plt.close(fig)


def _row(label: str, stats: dict) -> str:
    return (
        f"| {label} | {stats['pages']} | {stats['wall']:.2f} | {stats['fetch']:.2f} | "
        f"{stats['blocked']:.2f} | {stats['avg_blocked_workers']:.1f} | "
        f"{stats['pages_per_s']:.1f} |"
    )


def write_markdown(results: dict) -> None:
    sync = results["sync"]
    workers = results["workers"]
    mt = {r["num_workers"]: r for r in results["multithreaded"]}
    aio = {r["num_workers"]: r for r in results["async"]}
    uv = {r["num_workers"]: r for r in results["async_uvloop"]}

    mt_rows = "\n".join(_row(str(n), mt[n]) for n in workers)
    aio_rows = "\n".join(_row(str(n), aio[n]) for n in workers)
    uv_rows = "\n".join(_row(str(n), uv[n]) for n in workers)

    fastest_mt = min(results["multithreaded"], key=lambda r: r["wall"])
    fastest_aio = min(results["async"], key=lambda r: r["wall"])
    fastest_uv = min(results["async_uvloop"], key=lambda r: r["wall"])
    worker_list = ", ".join(str(n) for n in workers)
    pages = sync["pages"]

    MARKDOWN_PATH.write_text(
        f"""# Crawler comparison

Crawl of `{results["start_url"]}` ({pages} pages) with the sync, multithreaded, and async implementations.
Worker counts are powers of two from 1 to 256: `{worker_list}`.

![wall, fetch, and blocked time vs num_workers](crawler_comparison.svg)

## Metrics

| Metric | Meaning |
|---|---|
| **wall** | Elapsed time for the whole crawl. |
| **fetch** | Sum of per-request durations (I/O wait + HTML parse). Concurrent crawlers overlap these, so fetch stays large while wall drops. |
| **blocked** | Cumulative seconds OS threads spent inside blocking `get_html` / `urlopen`. Async I/O yields the event loop, so this stays 0. |
| **avg blocked** | `blocked / wall` — average number of threads stuck in `urlopen` during the crawl. |

## Sync baseline

| crawler | pages | wall (s) | fetch (s) | blocked (s) | avg blocked | pages/s |
|---|---:|---:|---:|---:|---:|---:|
{_row("sync", sync)}

One thread, so wall ≈ fetch ≈ blocked.

## Multithreaded

| workers | pages | wall (s) | fetch (s) | blocked (s) | avg blocked | pages/s |
|---|---:|---:|---:|---:|---:|---:|
{mt_rows}

Best wall: **{fastest_mt["wall"]:.2f}s** at `{fastest_mt["num_workers"]}` workers
({sync["wall"] / fastest_mt["wall"]:.1f}× vs sync). Blocked time stays near the sync fetch total because every GET still occupies a thread in `urlopen`.

## Async (stdlib event loop)

| workers | pages | wall (s) | fetch (s) | blocked (s) | avg blocked | pages/s |
|---|---:|---:|---:|---:|---:|---:|
{aio_rows}

Best wall: **{fastest_aio["wall"]:.2f}s** at `{fastest_aio["num_workers"]}` workers
({sync["wall"] / fastest_aio["wall"]:.1f}× vs sync). Fetch time is still the sum of in-flight awaits; **blocked stays 0** because `aiohttp` yields instead of parking an OS thread on each GET.

## Async + uvloop

Same crawler, but `asyncio.run(..., loop_factory=uvloop.new_event_loop)` so libuv drives the event loop instead of the stdlib selector.

| workers | pages | wall (s) | fetch (s) | blocked (s) | avg blocked | pages/s |
|---|---:|---:|---:|---:|---:|---:|
{uv_rows}

Best wall: **{fastest_uv["wall"]:.2f}s** at `{fastest_uv["num_workers"]}` workers
({sync["wall"] / fastest_uv["wall"]:.1f}× vs sync, {fastest_aio["wall"] / fastest_uv["wall"]:.2f}× vs stdlib asyncio).
Blocked stays 0: uvloop does not change the I/O model, only the loop implementation.

## Reading the plot

- **Wall** falls for both concurrent crawlers until the BFS frontier and the remote host saturate (around 64–128 workers here). Extra workers past that point do not help.
- **Fetch** is total request-seconds of work. For threads it stays near the sync baseline. Async fetch is lower because `aiohttp` reuses a connection pool; it rises again at high concurrency as the host slows down.
- **Blocked** is the difference that async buys you. Threads overlap I/O the same way async does, but they pay for it by sitting in `urlopen`. The event loop does not.
- Async with 1 worker is already faster than sync: that gap is the HTTP client (`aiohttp` vs `urlopen`), not concurrency.
- **uvloop** vs stdlib asyncio is event-loop overhead, not blocking vs non-blocking. On this host-bound crawl the two stay close; uvloop helps more when the loop itself is the bottleneck (many short I/O ops, not one slow website).

Rerun with `uv run python benchmark.py`. Delete `{RESULTS_PATH.name}` first to remeasure every crawler.
"""
    )


if __name__ == "__main__":
    main()
