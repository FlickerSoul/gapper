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
