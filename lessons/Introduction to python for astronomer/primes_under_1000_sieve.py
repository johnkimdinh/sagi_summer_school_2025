#!/usr/bin/env python3
"""primes_under_1000_sieve.py
Find and print all prime numbers below 1000 using the Sieve of Eratosthenes,
and report the elapsed wall‑clock time.
"""

import time

def sieve(limit: int) -> list[int]:
    """Return a list of all primes < *limit* using the classic sieve."""
    if limit < 2:
        return []
    # Boolean array: True means 'assume prime' initially
    is_prime = [True] * limit
    is_prime[0:2] = [False, False]  # 0 and 1 are not prime

    for p in range(2, int(limit ** 0.5) + 1):
        if is_prime[p]:
            # Mark multiples of p starting at p*p
            is_prime[p * p : limit : p] = [False] * len(range(p * p, limit, p))

    return [n for n, prime in enumerate(is_prime) if prime]

def main() -> None:
    start = time.perf_counter()
    primes = sieve(1000)
    elapsed = time.perf_counter() - start

    print("Primes below 1000:")
    print(primes)
    print(f"\nFound {len(primes)} primes in {elapsed:.6f} s")

if __name__ == "__main__":
    main()
