"""
Sync vs async, side by side.

Three runs do the same work: N greetings, each waiting DELAY seconds in the
middle. Only the waiting strategy differs -- blocking, awaited one at a time,
then all at once.
"""

import asyncio
import time

GREETINGS = 5
DELAY = 1.0


def greet_sync(n: int) -> None:
    print(f"  [{n}] Hello...")
    time.sleep(DELAY)
    print(f"  [{n}] World!")


async def greet_async(n: int) -> None:
    print(f"  [{n}] Hello...")
    await asyncio.sleep(DELAY)
    print(f"  [{n}] World!")


def run_sync() -> None:
    for n in range(1, GREETINGS + 1):
        greet_sync(n)


async def run_async_sequential() -> None:
    for n in range(1, GREETINGS + 1):
        await greet_async(n)


async def run_async_concurrent() -> None:
    async with asyncio.TaskGroup() as tg:
        for n in range(1, GREETINGS + 1):
            tg.create_task(greet_async(n))


def timed(label: str, fn) -> None:
    print(f"\n{label}")
    start = time.perf_counter()
    fn()
    print(f"-> {time.perf_counter() - start:.2f} sec")


if __name__ == "__main__":
    timed("sync", run_sync) # 5.02 sec
    timed("async, awaited one by one", lambda: asyncio.run(run_async_sequential())) # 5.02 sec
    timed("async, tasks created up front", lambda: asyncio.run(run_async_concurrent())) # 1.00 sec
