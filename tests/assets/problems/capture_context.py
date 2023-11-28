from gapper import problem, test_case
from gapper.core.types import CustomTestData


class GasStation:
    pass


def test_override(data: CustomTestData) -> None:
    gas_station = data.case.context.GasStation()
    sol_obj = data.solution(gas_station)
    sub_obj = data.submission(gas_station)
    data.case.assertEqual(sol_obj.gas_station, sub_obj.gas_station)

    data.result_proxy.set_pass_status("passed")


@test_case(gap_override_test=test_override)
@problem(context=("GasStation",))
class Car:
    def __init__(self, gas_station: GasStation):
        self.gas_station = gas_station


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": ("GasStation",),
    "easy_context": True,
    "extras": {},
}
