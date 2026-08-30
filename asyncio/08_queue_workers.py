"""
08 - Bounded concurrency: a queue and a fixed pool of workers.

RUN IT:   uv run --no-project --python 3.14 python asyncio/08_queue_workers.py
IT FAILS on elapsed time - nine items, one at a time.

WHAT'S WRONG
    Nothing is broken, exactly. It is just a for-loop. But "spawn a task per
    item" is not the right fix either: with 10,000 items you would open 10,000
    connections at once and fall over. You want a fixed number of workers
    pulling from a shared queue - the pattern behind every thread pool,
    job runner, and connection limit you will ever write.

YOUR JOB
    Process all nine items with exactly WORKERS concurrent workers.
    Under 0.55s, never more than 3 in flight at once, and 3 actually reached.

THINK ABOUT
    - asyncio.Queue: how does a worker block waiting for an item without
      blocking the loop? What ends the loop when the work runs out - a sentinel
      value per worker, or queue.join() plus cancelling the workers? Try both;
      the second is the idiom.
    - A Semaphore would also bound this. When would you prefer it to a queue?
      (Hint: who decides when work starts?)
    - The `in_flight` counter is deliberately unguarded. After exercise 07,
      convince yourself why it needs no lock here.
"""

import asyncio
import time

WORKERS = 3
ITEMS = [f"item-{i}" for i in range(9)]

processed: list[str] = []
in_flight = 0
max_in_flight = 0


async def handle(item: str) -> None:
    global in_flight, max_in_flight
    in_flight += 1
    max_in_flight = max(max_in_flight, in_flight)
    await asyncio.sleep(0.1)
    processed.append(item)
    in_flight -= 1


async def main() -> None:
    t0 = time.perf_counter()

    # <-- FIX ME: one at a time
    for item in ITEMS:
        await handle(item)

    elapsed = time.perf_counter() - t0
    print(f"elapsed: {elapsed:.2f}s  processed: {len(processed)}  peak: {max_in_flight}")

    assert sorted(processed) == sorted(ITEMS), "not every item was processed"
    assert max_in_flight <= WORKERS, f"{max_in_flight} in flight - pool is not bounded"
    assert max_in_flight == WORKERS, f"peak was {max_in_flight} - workers are idle"
    assert elapsed < 0.55, f"took {elapsed:.2f}s"
    print("PASS")


if __name__ == "__main__":
    asyncio.run(main())
