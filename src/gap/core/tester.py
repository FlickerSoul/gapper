from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Self, Callable, Any, Generic, List, TYPE_CHECKING, Generator

from dill import Unpickler, dump

from gap.core.configs.injection import InjectionConfig
from gap.core.errors import (
    SubmissionSyntaxError,
    TestFailedError,
    InternalError,
    NoSubmissionError,
    MultipleSubmissionError,
    MissingContextValueError,
    MultipleContextValueError,
)
from gap.core.problem import Problem, ProbOutputType, ProbInputType
from gap.core.test_result import TestResult

from gap.core.unittest_wrapper import ContextManager
from gap.core.utils import ModuleLoader

if TYPE_CHECKING:
    from gap.core.unittest_wrapper import RunnableTest


def _check_config_building_flag[**P, V, T: Callable[P, V]](fn: T) -> T:
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> V:
        self: TesterConfig = args[0]

        if self.is_building:
            raise RuntimeError("Cannot call this method while building config.")
        return fn(*args, **kwargs)

    return _wrapper


class ProblemUnpickler(Unpickler):
    def find_class(self, module: str, name: str) -> Any:
        match name:
            case "Problem":
                return Problem
            case "Tester":
                return Tester

        return super().find_class(module, name)


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


class Tester(ModuleLoader, Generic[ProbInputType, ProbOutputType]):
    def __init__(
        self,
        problem: Problem[ProbInputType, ProbOutputType],
        config: TesterConfig | None = None,
    ) -> None:
        self._problem: Problem[ProbInputType, ProbOutputType] = problem
        self._tester_config: TesterConfig = config or TesterConfig()
        self._submission: Any | None = None
        self._submission_context: ContextManager = ContextManager()

    @property
    def problem(self) -> Problem[ProbInputType, ProbOutputType]:
        return self._problem

    @problem.setter
    def problem(self, prob: Problem) -> None:
        self._problem = prob

    @property
    def tester_config(self) -> TesterConfig:
        return self._tester_config

    @property
    def submission(self) -> Any | None:
        return self._submission

    @property
    def submission_context(self) -> ContextManager:
        return self._submission_context

    def build(self) -> Self:
        self.tester_config.start_building()
        return self

    def __enter__(self) -> Self:
        return self

    def _finish_building_config(self) -> None:
        self.tester_config.finish_building()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._finish_building_config()

    def _load_script_submission_from_path(
        self, path: Path
    ) -> Generator[Callable[[], None], None, None]:
        if path.is_dir():
            for sub_path in path.iterdir():
                yield from self._load_script_submission_from_path(sub_path)
        else:
            if path.suffix != ".py":
                return None

            spec, md = self._load_module_spec_and_module(path)

            def run_script() -> None:
                assert spec.loader is not None
                spec.loader.exec_module(md)

            yield run_script

    def _load_object_submission_from_path(self, path: Path) -> Any:
        if path.is_dir():
            for sub_path in path.iterdir():
                yield from self._load_object_submission_from_path(sub_path)
        else:
            if path.suffix != ".py":
                return None

            spec, md = self._load_module_spec_and_module(path)
            spec.loader.exec_module(md)

            self.load_context_from_module(md)
            try:
                yield self._load_symbol_from_module(
                    md, self.problem.expected_submission_name
                )
            except AttributeError:
                return None

    def load_submission_from_path(self, path: Path) -> Self:
        if self.problem.config.is_script:
            submission_list = list(self._load_script_submission_from_path(path))
        else:
            submission_list = list(self._load_object_submission_from_path(path))

        if len(submission_list) == 0:
            raise NoSubmissionError()
        elif len(submission_list) > 1:
            raise MultipleSubmissionError()

        return self

    def load_context_from_module(self, md: ModuleType) -> Self:
        for context_value_name in self.problem.config.captured_context:
            try:
                context_value = self._load_symbol_from_module(md, context_value_name)
            except AttributeError:
                continue

            if context_value_name in self.submission_context:
                raise MultipleContextValueError(context_value_name)

            self.submission_context[context_value_name] = context_value

        return self

    def check_context_completeness(self) -> None:
        for context_value_name in self.problem.config.captured_context:
            if context_value_name not in self.submission_context:
                raise MissingContextValueError(context_value_name)

    def run(self) -> List[TestResult]:
        if self.problem is None:
            raise InternalError("No problem loaded.")

        if self.submission is None:
            raise InternalError("No submission loaded.")

        self.check_context_completeness()

        test_results: List[TestResult] = []

        for test in self.problem.generate_tests():
            test_results.append(
                test.load_context(self.submission_context).run_test(
                    deepcopy(self.submission),
                    TestResult(default_name=test.test_param.format()),
                )
            )

        return test_results

    @classmethod
    def from_file(cls, path: Path) -> Tester:
        with open(path, "rb") as f:
            tester = ProblemUnpickler(f).load()

        return tester

    def dump_to(self, path: Path) -> None:
        with open(path, "wb") as f:
            dump(self, f)
