from gapper import gs_connect, problem, test_case, test_cases


@test_cases.params([1, 2], [3, 4], [5, 6])
@test_case(2, 2, gap_expect=3)
@test_case(1, 2, gap_expect=3)
@gs_connect("https://www.gradescope.com/courses/668225/assignments/3674341/")
@problem()
def add(a: int, b: int) -> int:
    return a + b
