from gapper import post_test, problem, test_cases
from gapper.core.result_synthesizer import ResultSynthesizer
from gapper.core.test_result import TestResult


def check_at_least_half_is_correct(
    synthesizer: ResultSynthesizer, result_proxy: TestResult
) -> None:
    if (
        sum(result.is_passed for result in synthesizer.results)
        > len(synthesizer.results) // 2
    ):
        result_proxy.set_max_score(0)
        result_proxy.set_pass_status("passed")

        result_proxy.set_extra_points(5)


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
}
