"""
01 - A coroutine is an object, not a running thing.

RUN IT:   uv run --no-project --python 3.14 python asyncio/01_coroutines.py
IT FAILS. Read the AssertionError, and the RuntimeWarning printed with it.

WHAT'S WRONG
    Calling an `async def` function does not execute its body. It builds a
    coroutine object and hands it back to you, inert. Something has to drive it.

YOUR JOB
    Make main() print and assert the actual string "hello world".
    Do not modify greet().

THINK ABOUT
    - Who is allowed to `await`? Can a plain `def` do it?
    - What single function takes a coroutine and runs it to completion from
      ordinary synchronous code?
    - The RuntimeWarning is telling you the fate of a coroutine nobody drove.
      You will see that warning again in real code. Learn to recognise it now.
"""

import asyncio


async def greet(name: str) -> str:
    return f"hello {name}"


def main() -> None:
    result = greet("world")  # <-- FIX ME
    print(f"got: {result!r}")
    assert result == "hello world", f"expected 'hello world', got {result!r}"
    print("PASS")


if __name__ == "__main__":
    main()
