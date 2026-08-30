"""
09 - `async with` and `async for`: when setup and iteration are themselves I/O.

RUN IT:   uv run --no-project --python 3.14 python asyncio/09_async_with_for.py
IT FAILS with a TypeError before any assertion runs.

WHAT'S WRONG
    Opening a connection is I/O. Closing it is I/O. Reading the next chunk is
    I/O. Plain `with` and `for` have no way to await, so Python needs async
    counterparts, driven by their own dunder methods.

YOUR JOB
    Make Connection usable with `async with`, and chunks() usable with
    `async for`. Both blocks below must pass, including the one that raises.

THINK ABOUT
    - Which two dunder methods does `async with` call? What are their sync
      equivalents named? Same question for `async for`.
    - Part 2 raises inside the block. Where must close() be called from for it
      to still run? This is exactly how you will guarantee a client socket gets
      closed when a handler blows up.
    - chunks() can be written as a class with __aiter__/__anext__, or as an
      `async def` with `yield` in it. Write it both ways once - the second is
      an async generator, and it is what you will reach for in practice.
"""

import asyncio

events: list[str] = []


class Connection:
    # <-- FIX ME: make this work with `async with`
    def __enter__(self) -> "Connection":
        events.append("open")
        return self

    def __exit__(self, *exc: object) -> None:
        events.append("close")


# <-- FIX ME: make this work with `async for`
def chunks(n: int):
    for i in range(n):
        yield f"chunk-{i}"


async def part1() -> None:
    async with Connection():
        async for chunk in chunks(3):
            await asyncio.sleep(0.01)
            events.append(chunk)

    print(f"part1 events: {events}")
    assert events == ["open", "chunk-0", "chunk-1", "chunk-2", "close"], events
    print("part1 PASS")


async def part2() -> None:
    events.clear()
    with_error = False
    try:
        async with Connection():
            raise RuntimeError("handler blew up")
    except RuntimeError:
        with_error = True

    print(f"part2 events: {events}")
    assert with_error, "the error should still reach the caller"
    assert events == ["open", "close"], f"connection leaked: {events}"
    print("part2 PASS")


async def main() -> None:
    await part1()
    await part2()
    print("PASS")


if __name__ == "__main__":
    asyncio.run(main())
