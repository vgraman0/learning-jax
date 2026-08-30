"""
02 - `await` is not concurrency. Tasks are.

RUN IT:   uv run --no-project --python 3.14 python asyncio/02_tasks.py
IT FAILS on elapsed time. The results are right; the wall clock is not.

WHAT'S WRONG
    Three downloads of 0.5s each take 1.5s. They ran one after another.
    `await` means "suspend me until this finishes, and let the loop run OTHER
    TASKS meanwhile" - but there are no other tasks here, so nothing overlaps.

YOUR JOB
    Get all three running at once. Total under 0.75s, same three results,
    still in a, b, c order.

THINK ABOUT
    - What turns a coroutine into something the loop schedules independently?
    - Watch the "start"/"done" print order before and after your fix. That
      interleaving IS the concurrency - the timing is just how you measure it.
    - There are at least two ways to do this. Try create_task first so you can
      see the two steps (schedule, then collect) as separate things.
"""

import asyncio
import time


async def download(name: str, seconds: float) -> str:
    print(f"  start {name}")
    await asyncio.sleep(seconds)
    print(f"  done  {name}")
    return f"{name}-payload"


async def main() -> None:
    t0 = time.perf_counter()

    # <-- FIX ME: these three run back to back
    a = await download("a", 0.5)
    b = await download("b", 0.5)
    c = await download("c", 0.5)

    results = [a, b, c]
    elapsed = time.perf_counter() - t0
    print(f"elapsed: {elapsed:.2f}s  results: {results}")

    assert results == ["a-payload", "b-payload", "c-payload"], results
    assert elapsed < 0.75, f"took {elapsed:.2f}s - still sequential"
    print("PASS")


if __name__ == "__main__":
    asyncio.run(main())
