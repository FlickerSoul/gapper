import random
from typing import Generator

__all__ = ["generate_multiple_two_numbers"]


def generate_multiple_two_numbers(n: int) -> Generator[tuple[int, int], None, None]:
    yield from ((random.randint(1, 100), random.randint(1, 100)) for _ in range(n))
