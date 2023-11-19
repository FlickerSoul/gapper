from gapper import gs_connect, problem, test_case
from gapper.core.problem.extras.gradescope_connect import GSConnectConfig


@test_case("1", "2")
@test_case("1", "2")
@gs_connect("112358", "2468")
@problem()
def string_connection(a: str, b: str) -> str:
    return a + b


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": (),
    "easy_context": True,
    "extras": {
        "gs_connect": GSConnectConfig("112358", "2468"),
    },
}
