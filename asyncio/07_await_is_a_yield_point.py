"""
07 - Single-threaded does not mean safe.

RUN IT:   uv run --no-project --python 3.14 python asyncio/07_await_is_a_yield_point.py
IT FAILS: the account is overdrawn to -100 from a starting balance of 100.

WHAT'S WRONG
    withdraw() checks the balance, awaits, and only then subtracts. Every one
    of the ten tasks runs its check before any of them reaches the subtraction,
    because the await hands control back to the loop in between. All ten see
    100 available. All ten withdraw.

    One thread, no preemption, and still a race. The rule: your invariants are
    safe *between* awaits, and every `await` is a place another task can see
    your half-finished state. "Where are my awaits?" is the async version of
    "what is my critical section?"

YOUR JOB
    At most five withdrawals succeed, the balance lands on 0, and it is never
    negative at any point.

THINK ABOUT
    - Do not just delete the await - real code has I/O there. Assume you cannot
      remove it. (This is why the sleep is here at all.)
    - asyncio ships the primitive you need, with a familiar name. Note it is
      NOT the one from `threading`, and it is not thread-safe. Why would a
      loop-local lock be cheaper than an OS one?
    - Now look back at your HTTP server's Router and Request objects. Do they
      have this problem? Why not - and would that still hold if you added a
      cache or a hit counter?
"""

import asyncio

balance = {"amount": 100}


async def withdraw(amount: int) -> bool:
    # <-- FIX ME: check and act are not atomic across the await
    if balance["amount"] >= amount:
        await asyncio.sleep(0)  # pretend: writing to a ledger
        balance["amount"] -= amount
        return True
    return False


async def main() -> None:
    results = await asyncio.gather(*(withdraw(20) for _ in range(10)))
    succeeded = sum(results)

    print(f"succeeded: {succeeded}  final balance: {balance['amount']}")
    assert balance["amount"] >= 0, f"overdrawn to {balance['amount']}"
    assert succeeded == 5, f"expected exactly 5 successful withdrawals, got {succeeded}"
    assert balance["amount"] == 0, balance["amount"]
    print("PASS")


if __name__ == "__main__":
    asyncio.run(main())
