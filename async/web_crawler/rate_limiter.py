import asyncio
import time


class RateLimiter:
    def __init__(self, rps=30):
        self._interval = 1 / rps
        self._lock = asyncio.Lock()
        self._next = 0.0

    async def acquire(self) -> float:
        async with self._lock:
            now = time.monotonic()
            wait = max(0.0, self._next - now)
            self._next = max(now, self._next) + self._interval
            if wait:
                await asyncio.sleep(wait)
            return wait
