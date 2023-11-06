import random

__all__ = ["generate_two_random_number"]


def generate_two_random_number():
    return random.randint(1, 100), random.randint(1, 100)
