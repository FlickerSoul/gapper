def adder(a, b) -> int:
    return a + b % 10


def add(a: int, b: int, the_adder) -> int:
    return the_adder(a, b)
