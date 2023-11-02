from gapper import problem, test_cases


@test_cases.singular_param_iter((2 * i for i in range(3)), gap_expect=True)
@test_cases.singular_param_iter((2 * i + 1 for i in range(3)), gap_expect=False)
@problem()
def is_even(n: int) -> bool:
    return n & 1 == 0


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": (),
}
