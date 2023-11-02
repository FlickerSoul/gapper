import ast
import inspect
from typing import Any, Tuple

from gapper import problem, test_case
from gapper.core.test_result import TestResult
from gapper.core.unittest_wrapper import TestCaseWrapper


def check_recursive_ast(fn):
    tree = ast.parse(inspect.getsource(fn))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == fn.__name__:
                    return True
    return False


def recursive_check(
    param: TestCaseWrapper,
    result_proxy: TestResult,
    solution,
    submission,
    sln_results: Tuple[Any, str | None],
    sub_results: Tuple[Any, str | None],
) -> None:
    if not check_recursive_ast(submission):
        result_proxy.set_score(result_proxy.max_score // 2)
        result_proxy.set_pass_status("failed")
        result_proxy.add_description(
            "Failed because recursive call not found in submission."
        )


@test_case(10, gap_post_checks=[recursive_check])
@problem()
def fib(n: int) -> int:
    if n == 0:
        return 1
    if n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": (),
}
