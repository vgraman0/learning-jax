"""
04 - When one job fails, what happens to its siblings?

RUN IT:   uv run --no-project --python 3.14 python asyncio/04_taskgroup.py
IT FAILS on the "leftovers" assertion.

WHAT'S WRONG
    gather() propagates the first exception to you immediately - but it does
    NOT cancel the other jobs. They carry on as orphans, still holding sockets
    and file handles, with nobody waiting for them or watching for their errors.
    The assertion catches this by asking the loop what is still pending after
    the error was handled.

YOUR JOB
    Make all of these true at once:
      - the ValueError reaches main and is handled
      - "slow" is cancelled, so it never reaches "slow finished"
      - "slow" still runs its `finally` cleanup
      - nothing is left pending afterwards

THINK ABOUT
    - Python 3.11+ has a construct whose entire purpose is "these tasks cannot
      outlive this block, and an error in one cancels the rest". Use it.
    - It raises a *group* of exceptions, not a bare one. How do you catch that?
      (Look up `except*`.) Why is a group the honest thing to raise here?
    - This is structured concurrency. The value is not tidiness - it is that a
      failure can no longer leave work running that you have stopped tracking.
"""

import asyncio

log: list[str] = []


async def job(name: str, delay: float, boom: bool = False) -> str:
    try:
        await asyncio.sleep(delay)
        if boom:
            raise ValueError(f"{name} exploded")
        log.append(f"{name} finished")
        return name
    finally:
        log.append(f"{name} cleaned up")


async def main() -> None:
    errors: list[str] = []

    # <-- FIX ME
    try:
        await asyncio.gather(
            job("fast", 0.05),
            job("boom", 0.10, boom=True),
            job("slow", 1.00),
        )
    except ValueError as e:
        errors.append(str(e))

    await asyncio.sleep(0.05)  # give any orphans a moment to show themselves
    leftovers = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    print(f"errors:    {errors}")
    print(f"log:       {log}")
    print(f"leftovers: {[t.get_name() for t in leftovers]}")

    assert errors == ["boom exploded"], errors
    assert not leftovers, f"{len(leftovers)} task(s) still running after the failure"
    assert "slow cleaned up" in log, "the cancelled job must still clean up"
    assert "slow finished" not in log, "slow should have been cancelled, not completed"
    print("PASS")


if __name__ == "__main__":
    asyncio.run(main())
