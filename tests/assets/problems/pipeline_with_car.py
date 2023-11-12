from gapper import problem, test_case
from gapper.core.pipeline_support import Constructor, Function, Property

constructor = Constructor()
move = Function("move")
x = Property("x")
y = Property("y")
tank = Property("tank")
fuel = Property("fuel")


@test_case.pipeline(
    constructor(0, 0, 100, 100),
    move(10, 10),
    fuel,
    x,
    y,
    move(15, 15),
    fuel,
    x,
    y,
)
@problem()
class Car:
    def __init__(self, x: int, y: int, tank: int, fuel: int) -> None:
        self.x = x
        self.y = y
        self.tank = tank
        self.fuel = fuel

    def move(self, x: int, y: int) -> bool:
        if ((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5 <= self.fuel:
            self.x = x
            self.y = y
            self.fuel -= ((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5
            return True

        return False


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": (),
    "easy_context": False,
    "gs_connect": None,
}
