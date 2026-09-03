"""
Chaining coroutines: a three-stage pipeline (fetch -> parse -> store) where
each stage consumes the previous stage's return value, so a chain can only
run in order.

Four items run two ways -- one chain at a time, then all chains at once --
with timestamped stage logs showing where the time goes.
"""

import asyncio
import json
import time
from typing import Any, Callable, Coroutine

ITEMS = ["alpha", "beta", "gamma", "delta"]

FETCH_DELAY = 1.0
PARSE_DELAY = 0.5
STORE_DELAY = 0.3

# Reset by timed() at the start of each run so log lines read 0.00 upward.
_start = time.perf_counter()


def elapsed() -> float:
    """Seconds since the current run began."""
    return time.perf_counter() - _start


def log(item: str, message: str) -> None:
    """Print one timestamped line, e.g. '[alpha] fetched (t=1.00s)'."""
    print(f"  [{item:<5}] {message:<8} (t={elapsed():.2f}s)")


# --- the three stages -------------------------------------------------------
# Each one sleeps, logs, and returns something the next stage consumes. The
# return values are the point: they are what force the ordering.


async def fetch(item: str) -> str:
    """Sleep FETCH_DELAY, then return a raw payload string for `item`."""
    await asyncio.sleep(FETCH_DELAY)
    log(item, "fetched")
    return f'{{"item": "{item}", "size": {len(item)}}}'


async def parse(raw: str) -> dict[str, Any]:
    """Sleep PARSE_DELAY, then turn the raw payload into a dict."""
    await asyncio.sleep(PARSE_DELAY)
    parsed = json.loads(raw)
    log(parsed["item"], "parsed")
    return parsed


async def store(parsed: dict[str, Any]) -> str:
    """Sleep STORE_DELAY, then return a confirmation string."""
    await asyncio.sleep(STORE_DELAY)
    log(parsed["item"], "stored")
    return f"Stored parsed string: {parsed}"


# --- the chain --------------------------------------------------------------


async def pipeline(item: str) -> str:
    """Await the three stages in order, threading each result into the next.
    """
    raw = await fetch(item)
    parsed = await parse(raw)
    confirmation = await store(parsed)

    return confirmation


# --- the two drivers --------------------------------------------------------


async def run_sequential() -> list[str]:
    """Await one full pipeline at a time. Expect ~7.2 sec."""
    processed_items = []

    for item in ITEMS:
        processed_items.append(await pipeline(item))
    return processed_items


async def run_concurrent() -> list[str]:
    """Run every pipeline at once and collect the confirmations. Expect ~1.8 sec.
    """
    return await asyncio.gather(*[pipeline(item) for item in ITEMS])


def timed(label: str, main: Callable[[], Coroutine[Any, Any, list[str]]]) -> None:
    """Reset the clock, run `main` to completion, print the results and total."""
    global _start

    print(f"\n{label}")
    _start = time.perf_counter()
    results = asyncio.run(main())
    total = elapsed()  # read it before printing, so I/O isn't on the clock

    for line in results:
        print(f"  {line}")
    print(f"-> {total:.2f} sec")


if __name__ == "__main__":
    timed("one chain at a time", run_sequential)  # 7.21 sec
    timed("all chains at once", run_concurrent)  # 1.80 sec
