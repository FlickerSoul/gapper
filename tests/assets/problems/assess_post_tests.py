from typing import List

from gapper import post_test, problem, test_cases
from gapper.core.test_result import TestResult
from gapper.gradescope.datatypes.gradescope_meta import (
    GradescopeSubmissionMetadata,
)


def check_at_least_half_is_correct(
    test_results: List[TestResult],
    test_proxy: TestResult,
    metadata: GradescopeSubmissionMetadata | None,
) -> None:
    test_proxy.set_max_score(0)
    # if the number of passed tests is greater than half of the total number of tests
    if sum(result.is_passed for result in test_results) > len(test_results) // 2:
        test_proxy.set_pass_status("passed")

        test_proxy.set_extra_points(5)


@test_cases.singular_param_iter([i for i in range(10)], gap_max_score=1)
@post_test(check_at_least_half_is_correct)
@problem()
def square(x: int | float) -> int | float:
    return x**2


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": (),
    "easy_context": False,
    "extras": {},
}
