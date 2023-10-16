from gap import problem, test_case


@test_case("-1")
@test_case("10")
@problem(is_script=True)
def input_script() -> None:
    number_input = input("hello world! Please input a number: ")
    the_number = int(number_input)
    print(f"you inputted {the_number} and its square is {number_input}")


__problem_config__ = {
    "is_script": True,
    "check_stdout": True,
    "mock_input": True,
    "captured_context": (),
}
