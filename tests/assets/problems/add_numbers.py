from gapper import problem, test_case, test_cases


@test_cases.params([1, 2], [3, 4])
@test_case(1, 2)
@test_case(3, 4)
@problem()
def add_numbers(a: int, b: int) -> int:
    return a + b


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": (),
    "easy_context": False,
    "extras": {},
}
