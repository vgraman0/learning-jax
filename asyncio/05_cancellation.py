"""
05 - Cancellation is an exception, and you can wrongly swallow it.

RUN IT:   uv run --no-project --python 3.14 python asyncio/05_cancellation.py
IT FAILS: part 1 says the task swallowed its cancellation.

WHAT'S WRONG
    task.cancel() does not kill anything. It arranges for CancelledError to be
    raised inside the coroutine at its next await point. That is all. A broad
    `except BaseException` catches it, the coroutine carries on to a normal
    return, and the cancellation quietly did nothing.

    Since Python 3.8 CancelledError inherits from BaseException, not Exception,
    specifically so that ordinary `except Exception:` handlers do not eat it.

YOUR JOB
    Part 1: cleanup must still run, AND the task must end up genuinely
            cancelled (task.cancelled() is True).
    Part 2: implement fetch_with_timeout so a 5s operation gives up after 0.2s,
            raising TimeoutError, with its cleanup run.

THINK ABOUT
    - Where does cleanup belong if you are not allowed to swallow the error?
    - If you must catch CancelledError to clean up, what is the last line of
      that handler obliged to be?
    - Part 2: asyncio has a context manager for deadlines (3.11+). Note it
      raises TimeoutError, not CancelledError - what converts one to the other,
      and why is that distinction useful to a caller?
    - Every timeout, every shutdown, and every "client hung up" you will ever
      handle is built on this mechanism. It is worth the extra ten minutes.
"""

import asyncio


async def worker(state: dict) -> None:
    try:
        while True:
            await asyncio.sleep(0.05)
            state["ticks"] += 1
    except BaseException:  # <-- FIX ME
        state["cleaned"] = True


async def part1() -> None:
    state = {"ticks": 0, "cleaned": False}
    task = asyncio.create_task(worker(state))
    await asyncio.sleep(0.2)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    print(f"part1 state: {state}  cancelled={task.cancelled()}")
    assert state["ticks"] > 0, "worker never ran"
    assert state["cleaned"], "cleanup did not run"
    assert task.cancelled(), "task swallowed the cancellation instead of honouring it"
    print("part1 PASS")


async def slow_fetch(state: dict) -> str:
    try:
        await asyncio.sleep(5)
        return "payload"
    finally:
        state["closed"] = True


async def fetch_with_timeout(state: dict) -> str:
    # <-- FIX ME: give up after 0.2s
    return await slow_fetch(state)


async def part2() -> None:
    state = {"closed": False}
    timed_out = False
    try:
        await fetch_with_timeout(state)
    except TimeoutError:
        timed_out = True

    print(f"part2 state: {state}  timed_out={timed_out}")
    assert timed_out, "expected TimeoutError after 0.2s"
    assert state["closed"], "the abandoned operation must still clean up"
    print("part2 PASS")


async def main() -> None:
    await part1()
    await part2()
    print("PASS")


if __name__ == "__main__":
    asyncio.run(main())
