from gapper import problem, tc, tcs

one_point_tc = tc.bind(gap_max_score=1)
one_point_tcs = tcs.bind(gap_max_score=1)


@one_point_tcs.params([3, 4], [5, 6])
@one_point_tc(1, 2)
@problem()
def multiply(x: int, y: int) -> int:
    return x * y


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": (),
    "easy_context": True,
    "extras": {},
}
