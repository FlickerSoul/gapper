from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Generator, Generic, List, Self

from dill import Unpickler, dump

from gapper.core.errors import (
    InternalError,
    MissingContextValueError,
    MultipleContextValueError,
    MultipleSubmissionError,
    NoSubmissionError,
)
from gapper.core.problem import ProbInputType, Problem, ProbOutputType
from gapper.core.test_result import TestResult
from gapper.core.unittest_wrapper import ContextManager
from gapper.core.utils import ModuleLoader

if TYPE_CHECKING:
    from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata


class ProblemUnpickler(Unpickler):
    def find_class(self, module: str, name: str) -> Any:
        match name:
            case "Problem":
                return Problem
            case "Tester":
                return Tester

        return super().find_class(module, name)


class Tester(ModuleLoader, Generic[ProbInputType, ProbOutputType]):
    def __init__(
        self,
        problem: Problem[ProbInputType, ProbOutputType],
    ) -> None:
        self._problem: Problem[ProbInputType, ProbOutputType] = problem
        self._submission: Any | None = None
        self._submission_context: ContextManager = ContextManager()

    @property
    def problem(self) -> Problem[ProbInputType, ProbOutputType]:
        return self._problem

    @problem.setter
    def problem(self, prob: Problem) -> None:
        self._problem = prob

    @property
    def submission(self) -> Any | None:
        return self._submission

    @property
    def submission_context(self) -> ContextManager:
        return self._submission_context

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

            spec, md = self._load_module_spec_and_module(path, exec_mod=True)

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

        self._submission = submission_list[0]

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

    def run(
        self, metadata: GradescopeSubmissionMetadata | None = None
    ) -> List[TestResult]:
        if self.problem is None:
            raise InternalError("No problem loaded.")

        if self.submission is None:
            raise InternalError("No submission loaded.")

        self.check_context_completeness()

        test_results: List[TestResult] = []

        for test in self.problem.generate_tests():
            test_results.append(
                test.load_metadata(metadata)
                .load_context(self.submission_context)
                .run_test(
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

    def dump_to(self, path: Path | str) -> None:
        with open(path, "wb") as f:
            dump(self, f)
