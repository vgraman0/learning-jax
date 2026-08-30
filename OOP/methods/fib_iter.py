from __future__ import annotations

# iterator protocol:
# `.__iter__()`: Called to initialize the iterator. It must return an iterator object.
# `.__next__()`: Called to iterate over the iterator. It must return the next value in the data stream.

class FibonacciIterator:
    def __init__(self, stop=10) -> None:
        self._stop = stop
        self._index = 0
        self._current = 0
        self._next = 1

    def __iter__(self) -> FibonacciIterator:
        return self

    def __next__(self) -> int:
        if self._index < self._stop:
            self._index += 1
            fib_number = self._current
            self._current, self._next = (
                self._next,
                self._current + self._next
            )
            return fib_number
        else:
            raise StopIteration


for fib_number in FibonacciIterator():
    print(fib_number)