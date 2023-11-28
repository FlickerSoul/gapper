from typing import Callable

from gapper import problem, test_case, test_cases
from gapper.core.types import CustomTestData, CustomTestFn


def factory() -> CustomTestFn:
    def my_adder(a, b) -> int:
        return a + b % 10

    adder: Callable[[int, int], int]

    def custom_test(
        data: CustomTestData,
    ):
        nonlocal adder
        assert data.solution(*data.case.test_param.args, my_adder) == data.submission(
            *data.case.test_param.args, adder
        )
        assert my_adder(*data.case.test_param.args) == adder(*data.case.test_param.args)

    return custom_test


@test_cases.param_iter(([i, i + 1] for i in range(10)), gap_override_test=factory())
@test_case(1, 2, gap_override_test=factory())
@problem(context=["adder"], easy_context=True)
def add(a: int, b: int, the_adder) -> int:
    return the_adder(a, b)


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": ["adder"],
    "easy_context": True,
    "extras": {},
}
