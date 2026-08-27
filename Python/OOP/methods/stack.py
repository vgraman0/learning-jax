from __future__ import annotations

from collections.abc import Iterator, Iterable
from typing import Self, overload

class Stack[T]:
    def __init__(self, items: Iterable[T] | None = None) -> None:
        self.items: list[T] = list(items) if items is not None else []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()
    
    def __contains__(self, item: object) -> bool:
        return item in self.items

    def __add__(self, other) -> Stack:
        return type(self)(self.items + other.items)
    
    def __iadd__(self, other) -> Stack:
        self.items.extend(other.items)
        return self

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.items!r})"

    def __iter__(self) -> Iterator:
        return iter(self.items[::-1])

    def __len__(self):
        return len(self.items)
