from typing import List, Generator


# Fibonacci is infinite, but this method can only return a finite list.
def fib(n: int) -> List[int]:
    numbers = []
    current, next = 0, 1
    while len(numbers) < n:
        current, next = next, current + next
        numbers.append(current)

    return numbers

def fib_gen() -> Generator[int, None, None]:
    current, next = 0, 1
    while True:
        current, next = next, current + next
        yield current

result = fib_gen()
for n in result:
    print(n, end=', ')
    if n > 10000:
        break

print("Done")
