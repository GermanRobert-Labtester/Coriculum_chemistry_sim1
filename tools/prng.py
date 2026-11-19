#!/usr/bin/env python3
"""N05 deterministic PRNG (Python twin): SplitMix64 (splitmix64-u64-v1).

NON-CRYPTOGRAPHIC: For reproducible sampling, form assembly, and test vectors
only. Never use for security, tokens, authentication, or proctoring.

Standard library only (no random module). Mirrors src/prng.js bit-for-bit
using unsigned 64-bit integer arithmetic masked with MASK_64.
"""
from __future__ import annotations

from typing import Iterable, Sequence, TypeVar

T = TypeVar('T')

ALGORITHM_ID = 'splitmix64-u64-v1'
MASK_64 = 0xFFFFFFFFFFFFFFFF
U64_MOD = 1 << 64
GAMMA = 0x9E3779B97F4A7C15
MUL1 = 0xBF58476D1CE4E5B9
MUL2 = 0x94D049BB133111EB
SHIFT1 = 30
SHIFT2 = 27
SHIFT3 = 31


class PrngError(ValueError):
    """Named deterministic PRNG error matching src/prng.js error codes."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f'[{code}] {message}')
        self.code = code
        self.message = message


def _validate_seed(seed: object) -> int:
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise PrngError('E_PRNG_INVALID_SEED', f'Seed must be a positive 64-bit integer, got {type(seed).__name__}.')
    if seed < 1 or seed > MASK_64:
        raise PrngError('E_PRNG_INVALID_SEED', f'Seed {seed} out of legal range [1, {MASK_64}].')
    return seed


def _validate_bound(bound: object) -> int:
    if isinstance(bound, bool) or not isinstance(bound, int):
        raise PrngError('E_PRNG_INVALID_BOUND', f'Bound must be a positive integer, got {type(bound).__name__}.')
    if bound < 1 or bound > U64_MOD:
        raise PrngError('E_PRNG_INVALID_BOUND', f'Bound {bound} out of legal range [1, {U64_MOD}].')
    return bound


class SplitMix64:
    """Deterministic SplitMix64 integer stream."""

    algorithm_id = ALGORITHM_ID

    def __init__(self, seed: int) -> None:
        self._seed = _validate_seed(seed)
        self._state = self._seed
        self._draws = 0

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def state(self) -> int:
        return self._state

    def draws_count(self) -> int:
        return self._draws

    def next_u64(self) -> int:
        self._state = (self._state + GAMMA) & MASK_64
        self._draws += 1
        z = self._state
        z = ((z ^ (z >> SHIFT1)) * MUL1) & MASK_64
        z = ((z ^ (z >> SHIFT2)) * MUL2) & MASK_64
        z = z ^ (z >> SHIFT3)
        return z & MASK_64

    def next_int(self, bound: int) -> int:
        b = _validate_bound(bound)
        threshold = (U64_MOD - b) % b
        while True:
            r = self.next_u64()
            if r >= threshold:
                return r % b

    def next_range(self, min_inclusive: int, max_inclusive: int) -> int:
        if (isinstance(min_inclusive, bool) or not isinstance(min_inclusive, int)
                or isinstance(max_inclusive, bool) or not isinstance(max_inclusive, int)):
            raise PrngError('E_PRNG_INVALID_BOUND', 'Range bounds must be integers.')
        if min_inclusive > max_inclusive:
            raise PrngError('E_PRNG_INVALID_BOUND', f'min_inclusive ({min_inclusive}) > max_inclusive ({max_inclusive}).')
        span = max_inclusive - min_inclusive + 1
        return min_inclusive + self.next_int(span)

    def shuffle(self, items: Sequence[T] | Iterable[T]) -> list[T]:
        arr = list(items)
        for i in range(len(arr) - 1, 0, -1):
            j = self.next_int(i + 1)
            arr[i], arr[j] = arr[j], arr[i]
        return arr


def create_stream(seed: int) -> SplitMix64:
    return SplitMix64(seed)
