from gap import problem, test_case


@test_case("1", "2")
@test_case("-1.2", "5.7")
@problem(check_stdout=True, mock_input=True)
def check_output_and_stdout() -> int:
    a = input("the first number: ")
    b = input("the second number: ")
    int_product = int(float(a) * float(b))
    print(f"the product of {a} and {b} is {int_product}")
    return int_product


__problem_config__ = {
    "is_script": False,
    "check_stdout": True,
    "mock_input": True,
    "captured_context": (),
}
