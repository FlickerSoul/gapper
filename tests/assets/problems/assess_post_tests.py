from gapper import post_tests, problem, test_cases
from gapper.core.types import PostTestsData


def check_at_least_half_is_correct(data: PostTestsData) -> None:
    # if the number of passed tests is greater than half of the total number of tests
    if (
        sum(result.is_passed for result in data.test_results)
        > len(data.test_results) // 2
    ):
        data.result_proxy.set_pass_status("passed")


@test_cases.singular_param_iter([i for i in range(10)], gap_max_score=1)
@post_tests(check_at_least_half_is_correct, gap_max_score=0, gap_extra_points=5)
@problem()
def square(x: int | float) -> int | float:
    return x**2


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": (),
    "easy_context": True,
    "extras": {},
}
