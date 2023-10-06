from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self, Callable, Any, Generic

from gap.core.configs.injection import InjectionConfig
from gap.core.problem import Problem, ProbOutputType, ProbInputType


def _check_config_building_flag[**P, V, T: Callable[P, V]](fn: T) -> T:
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> V:
        self: TesterConfig = args[0]

        if self.is_building:
            raise RuntimeError("Cannot call this method while building config.")
        return fn(*args, **kwargs)

    return _wrapper


@dataclass
class TesterConfig:
    _is_building: bool = False
    _injection_config: InjectionConfig = field(default_factory=InjectionConfig)

    def start_building(self) -> None:
        self._is_building = True

    def finish_building(self) -> None:
        self._is_building = False

    @property
    def is_building(self) -> bool:
        return self._is_building

    @property
    def injection_config(self) -> InjectionConfig:
        return self._injection_config

    @injection_config.setter
    @_check_config_building_flag
    def injection_config(self, value: InjectionConfig) -> None:
        self._injection_config = value


class Tester(Generic[ProbInputType, ProbOutputType]):
    def __init__(
        self,
        config: TesterConfig | None = None,
    ) -> None:
        self._problem: Problem[ProbInputType, ProbOutputType] | None = None
        self._tester_config: TesterConfig = config or TesterConfig()

    @property
    def problem(self) -> Problem[ProbInputType, ProbOutputType] | None:
        return self._problem

    @problem.setter
    def problem(self, prob: Problem) -> None:
        self._problem = prob

    @property
    def tester_config(self) -> TesterConfig:
        return self._tester_config

    def build(self) -> Self:
        self.tester_config.start_building()
        return self

    def __enter__(self) -> Self:
        return self

    def _finish_building_config(self) -> None:
        self.tester_config.finish_building()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._finish_building_config()
