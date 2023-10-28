from gapper import problem, test_case, test_cases


@test_cases.params([1.5, 2], [3.2, 4])
@test_case(1, 2)
@test_case(1.5, 3.5)
@problem(check_stdout=True)
def check_output_and_stdout(a: float, b: float) -> int:
    int_product = int(a * b)
    print(f"the product of {a} and {b} is {int_product}")
    return int_product


__problem_config__ = {
    "is_script": False,
    "check_stdout": True,
    "mock_input": False,
    "captured_context": (),
}
