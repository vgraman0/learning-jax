"""
03 - The cardinal sin: a blocking call inside a coroutine.

RUN IT:   uv run --no-project --python 3.14 python asyncio/03_blocking.py
IT FAILS on elapsed time - even though this file already uses tasks correctly.

WHAT'S WRONG
    checksum() is synchronous CPU/disk-shaped work. It does not await, so the
    event loop cannot take control back while it runs. One task hogs the single
    thread and every other task is frozen behind it. No error, no warning - just
    concurrency that silently isn't there.

    This is the most important failure mode in asyncio, and the one you will
    hit for real when the HTTP challenge asks you to read files.

YOUR JOB
    Keep checksum() exactly as it is - pretend it is library code you cannot
    change. Get total time under 0.55s.

THINK ABOUT
    - You cannot make a blocking function non-blocking. So where else could it
      run, such that the loop stays free?
    - asyncio has a one-line answer for exactly this. Find it.
    - Afterwards: does that answer help if the work were 30 seconds of pure CPU
      across 100 connections? Why not? What is different about I/O?
"""

import asyncio
import time


def checksum(name: str) -> str:
    """Synchronous, blocking. Imagine a file read or a gzip pass."""
    time.sleep(0.3)
    return f"{name}-sum"


async def job(name: str) -> str:
    await asyncio.sleep(0.05)  # some real async I/O
    return checksum(name)  # <-- FIX ME: this blocks the whole loop


async def main() -> None:
    t0 = time.perf_counter()
    results = await asyncio.gather(job("a"), job("b"), job("c"))
    elapsed = time.perf_counter() - t0
    print(f"elapsed: {elapsed:.2f}s  results: {results}")

    assert results == ["a-sum", "b-sum", "c-sum"], results
    assert elapsed < 0.55, (
        f"took {elapsed:.2f}s - the tasks are fine, something is blocking the loop"
    )
    print("PASS")


if __name__ == "__main__":
    asyncio.run(main())
