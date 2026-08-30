# asyncio exercises

Ten drills plus a capstone, in order. Each one is a small program that **runs,
fails, and tells you why**. Fix the file until it prints `PASS`.

Run from the `python-notes` root:

```
uv run --no-project --python 3.14 python asyncio/01_coroutines.py
```

`--no-project` skips syncing the JAX/NumPy dependencies - these exercises are
pure stdlib and need none of them. `--python 3.14` is what exercise 10 part B
wants; everything else works on 3.12+, so a bare `python` from this repo's venv
is fine for 01-09 if you prefer.

No solutions are included, on purpose - every file has a `THINK ABOUT` section
instead. Ask if you want the answer to a specific one.

| # | File | The lesson |
|---|------|-----------|
| 01 | `01_coroutines.py` | Calling `async def` runs nothing |
| 02 | `02_tasks.py` | `await` is sequential; tasks are what overlap |
| 03 | `03_blocking.py` | One blocking call freezes every connection, silently |
| 04 | `04_taskgroup.py` | A failure must not leave siblings orphaned |
| 05 | `05_cancellation.py` | Cancellation is an exception; timeouts are built on it |
| 06 | `06_lost_tasks.py` | Unheld tasks vanish; unawaited errors go unseen |
| 07 | `07_await_is_a_yield_point.py` | Single-threaded still races, across awaits |
| 08 | `08_queue_workers.py` | Bounded concurrency with a queue and N workers |
| 09 | `09_async_with_for.py` | `async with` / `async for`, and cleanup on error |
| 10 | `10_debugging.py` | Debug mode, and inspecting a live task tree |
| 11 | `11_capstone.md` | Build an echo server, then bridge to the HTTP server |

Exercises 02, 03 and 08 assert on wall-clock time. If your machine is heavily
loaded they can be flaky - rerun before believing a narrow failure.

03, 05 and 07 are the three that matter most for the HTTP server. If you only
do three, do those.

## Why these exist

Written while working out how to add concurrent connections to
`~/repos/codecrafters-http-server-python`, whose `Server.serve_forever` accepts
one connection, handles it to completion, and only then accepts the next - so a
client that connects and stays silent freezes every other client behind it.
Exercise 11 ends by bridging back to that code.

## One trap about this folder

It is named `asyncio`, which shadows the stdlib module if it ever becomes a
regular package. Right now it is safe: with no `__init__.py`, Python treats it
as a namespace package, and namespace packages lose to real modules on the path.

**Do not add an `__init__.py` here.** The moment you do, any `import asyncio`
resolved with this repo's root on `sys.path` finds this folder instead of the
standard library. That includes JupyterLab launched from `python-notes/`, which
would break the JAX and NumPy notebooks in a thoroughly confusing way, with a
traceback pointing at neither. (Verified - it really does happen.)

Renaming the folder to `asyncio_exercises` removes the hazard permanently if you
would rather not have to remember.
