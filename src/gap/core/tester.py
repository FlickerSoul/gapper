from __future__ import annotations

from dataclasses import dataclass
from typing import Self, Callable, Any

from gap.core.problem import Problem, ProbInputType, ProbOutputType


def _check_config_building_flag[T: Callable](fn: T) -> T:
    def _wrapper(self: Tester, *args: Any, **kwargs: Any) -> Any:
        if self.tester_config.is_building:
            raise RuntimeError("Cannot call this method while building config.")
        return fn(self, *args, **kwargs)

    return _wrapper


@dataclass
class TesterConfig:
    _is_building: bool = False

    def start_building(self) -> None:
        self._is_building = True

    def finish_building(self) -> None:
        self._is_building = False

    @property
    def is_building(self) -> bool:
        return self._is_building


class Tester:
    def __init__(
        self,
        problem: Problem[ProbInputType, ProbOutputType],
        config: TesterConfig | None = None,
    ) -> None:
        self.problem = problem
        self.tester_config: TesterConfig = config or TesterConfig()

    def build_config(self) -> Self:
        self.tester_config.start_building()
        return self

    def __enter__(self) -> Self:
        return Self

    def _finish_building_config(self) -> None:
        self.tester_config.finish_building()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._finish_building_config()

    @staticmethod
    def _check_config_building_flag(fn: Callable[..., Any]) -> Callable[..., Any]:
        def _wrapper(self: Tester, *args: Any, **kwargs: Any) -> Any:
            if self.tester_config._is_building:
                raise RuntimeError("Cannot call this method while building config.")
            return fn(self, *args, **kwargs)

        return _wrapper
