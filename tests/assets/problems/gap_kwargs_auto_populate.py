from gapper import problem, test_cases


@test_cases.params(
    [100, 1000],
    [10_000, 100_000],
    gap_name=["slightly large num", "large_num"],
    gap_weight=[1, 2],
)
@test_cases.params([-1, -2], [-3, -4], gap_name="negatives", gap_weight=2)
@test_cases.params([1, 2], [3, 4], [5, 6], [7, 8], gap_hidden=True)
@problem()
def mul(a: int, b: int) -> int:
    return a * b


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": (),
    "easy_context": True,
    "extras": {},
}
