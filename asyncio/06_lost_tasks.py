"""
06 - Tasks you don't hold on to, and errors nobody collects.

RUN IT:   uv run --no-project --python 3.14 python asyncio/06_lost_tasks.py
IT FAILS: no work was done, and the failure was never seen.

WHAT'S WRONG
    create_task() schedules work and returns immediately. Two things then go
    wrong here:

    1. main() returns straight away. asyncio.run() cancels everything still
       pending on the way out, so the jobs never finish. Nothing warns you -
       note that the output is empty rather than wrong, which is worse.
    2. Nobody ever awaits the task that raises. Its exception has no audience.
       You cannot see this yet, because bug 1 is hiding it: job "c" is
       cancelled before it ever reaches its raise. Add `await
       asyncio.sleep(0.3)` before the prints and run again. Now the jobs finish
       and the loop reports "Task exception was never retrieved" - that message
       is an error dying alone. In a server it is a request that failed with no
       log line and no response.

    There is a third trap not shown here: the loop keeps only a weak reference
    to a task, so a fire-and-forget task with no saved reference can be garbage
    collected mid-flight and simply vanish. Always keep a reference.

YOUR JOB
    All three jobs run to completion, and the failure of "c" is recorded in
    errors rather than lost.

THINK ABOUT
    - What has to happen between "schedule it" and "main returns"?
    - Fixing bug 1 with a bare sleep would make the timing assertion pass while
      leaving the error lost. Why is "wait long enough" never the fix?
    - Solve it once by hand (keep references, await them, catch the error), then
      solve it again with the construct from exercise 04. Which one makes it
      impossible to reintroduce this bug later?
"""

import asyncio

done: list[str] = []


async def job(name: str, boom: bool = False) -> str:
    await asyncio.sleep(0.1)
    if boom:
        raise RuntimeError(f"{name} failed")
    done.append(name)
    return name


async def main() -> None:
    errors: list[str] = []

    # <-- FIX ME: scheduled and immediately forgotten
    asyncio.create_task(job("a"))
    asyncio.create_task(job("b"))
    asyncio.create_task(job("c", boom=True))

    print(f"done:   {sorted(done)}")
    print(f"errors: {errors}")

    assert sorted(done) == ["a", "b"], f"expected a and b to finish, got {sorted(done)}"
    assert errors == ["c failed"], f"the failure of c was lost: {errors}"
    print("PASS")


if __name__ == "__main__":
    asyncio.run(main())
