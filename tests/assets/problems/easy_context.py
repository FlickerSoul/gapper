from typing import Callable

from gapper import problem, test_case, test_cases
from gapper.core.test_result import TestResult
from gapper.core.unittest_wrapper import TestCaseWrapper


def my_adder(a, b) -> int:
    return a + b % 10


adder: Callable[[int, int], int]  # adder is not defined here, this is just a type hint


def custom_test(param: TestCaseWrapper, result_proxy: TestResult, solution, submission):
    assert solution(*param.test_param.args, my_adder) == submission(
        *param.test_param.args,
        adder,  # notice here,
    )
    # adder is not defined, but we can use it
    # this is because it will be captured from students' submission context
    assert my_adder(*param.test_param.args) == adder(*param.test_param.args)


@test_cases.param_iter(([i, i + 1] for i in range(10)), gap_override_test=custom_test)
@test_case(1, 2, gap_override_test=custom_test)
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
