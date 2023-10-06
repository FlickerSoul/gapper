from __future__ import annotations

from pathlib import Path
from typing import Any

from dill import Unpickler

from gap.core.problem import Problem, ProbOutputType, ProbInputType
from gap.core.tester import Tester


class ProblemUnpickler(Unpickler):
    def find_class(self, module: str, name: str) -> Any:
        match name:
            case "Problem":
                return Problem
            case "Tester":
                return Tester

        return super().find_class(module, name)


def load_packed_tester(
    path: Path, filename: str = "tester.pckl"
) -> Problem[ProbInputType, ProbOutputType]:
    with open(path / filename, "rb") as problem_pickle:
        return ProblemUnpickler(problem_pickle).load()
