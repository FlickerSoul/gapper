from gapper import problem, test_case
from gapper.injection import (
    generate_multiple_two_numbers,
    generate_two_random_number,
)


@test_case(*generate_multiple_two_numbers(10))
@test_case(*generate_two_random_number())
@problem()
def power(a: int, b: int) -> int:
    return a**b
