"""
10 - Seeing inside a running loop. No assertions here; this one is observation.

PART A - catching a blocked loop automatically
    RUN IT:  uv run --no-project --python 3.14 python asyncio/10_debugging.py
    Watch for a warning like:
        Executing <Task ...> took 0.250 seconds

    Debug mode warns when a callback hogs the loop (default threshold 0.1s).
    This catches exercise 03's bug for you, in code you did not write and had
    no reason to suspect. Turn it on whenever something is mysteriously slow.

    Try:
      1. Note the warning.
      2. Fix rude_neighbour() the way you fixed exercise 03. Warning gone.
      3. Set debug=False and reintroduce the bug. Note that the program is
         still wrong and now says nothing at all. That silence is the danger.
      4. PYTHONASYNCIODEBUG=1 does the same without editing code:
         PYTHONASYNCIODEBUG=1 uv run --no-project --python 3.14 python asyncio/10_debugging.py

PART B - inspecting a live process
    Python 3.14 can introspect a running program's task tree from outside.
    RUN IT:  uv run --no-project --python 3.14 python asyncio/10_debugging.py hang
    It prints its PID and then hangs on purpose. In a second terminal:
        uv run --no-project --python 3.14 python -m asyncio ps <pid>
        uv run --no-project --python 3.14 python -m asyncio pstree <pid>
    (If those subcommands differ in your build: uv run --no-project --python 3.14 python -m asyncio --help)

    Read the tree. Find which coroutine each task is parked in, and on what.
    When a connection hangs in your HTTP server and you have no idea which of
    fifty tasks is stuck, this is how you find out. Ctrl-C to stop it.
"""

import asyncio
import os
import sys
import time


def rude_neighbour() -> None:
    time.sleep(0.25)  # blocks the loop; debug mode will tell on it


async def polite(name: str) -> None:
    for _ in range(3):
        await asyncio.sleep(0.05)
    print(f"  {name} done")


async def part_a() -> None:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(polite("a"))
        tg.create_task(polite("b"))
        tg.create_task(asyncio.to_thread(lambda: None))
        rude_neighbour()
    print("part A finished - look above for the slow-callback warning")


async def waiting_on_nothing(label: str) -> None:
    await asyncio.Event().wait()  # never set, on purpose


async def part_b() -> None:
    print(f"PID {os.getpid()} - hanging on purpose. Inspect me, then Ctrl-C.")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(waiting_on_nothing("reader"), name="reader")
        tg.create_task(waiting_on_nothing("writer"), name="writer")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "hang":
        asyncio.run(part_b())
    else:
        asyncio.run(part_a(), debug=True)
