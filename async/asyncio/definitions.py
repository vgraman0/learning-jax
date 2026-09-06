import asyncio
import time
from itertools import count

from hello_world import timed


def sync_function(test_param: str) -> str:
    print("This is a synchronous function.")

    time.sleep(0.1)

    return f"Sync Result: {test_param}"

# coroutine function
async def async_function(test_param: str) -> str:
    print("This is an asynchronous function.")

    await asyncio.sleep(0.1)

    return f"Async Result: {test_param}"

async def main():
    # sync_result = sync_function("Test")

    ## futures example
    # loop = asyncio.get_running_loop()
    # future = loop.create_future()
    # print(f"Empty Future: {future}")
    #
    # future.set_result("Future Result: Test")
    # future_result = await future
    # print(future_result)

    ## coroutines example
    # coroutine_obj = async_function("Test")
    # print(coroutine_obj)
    #
    # coroutine_result = await coroutine_obj
    # print(coroutine_result)

    # task
    # handed over to event loop, executed when it gets a chance
    # implemented as a future under the hood
    task = asyncio.create_task(async_function("Test"))
    print(task)

    task_result = await task
    print(task_result)

# coroutines: created when calling an async function
# tasks: wrappers around coroutines scheduled on event loop
# futures: low-level objects representing future results


if __name__ == "__main__":
    asyncio.run(main())