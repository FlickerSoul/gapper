"""This module contains the definition of the tester class."""
from __future__ import annotations

import logging
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


_tester_logger = logging.getLogger("gapper.tester")


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
        """Create a tester object.

        :param problem: The problem to be tested.
        """
        self._problem: Problem[ProbInputType, ProbOutputType] = problem
        self._submission: Any | None = None
        self._submission_context: ContextManager = ContextManager()
        self._logger = _tester_logger.getChild(
            f"Tester_{problem and problem.expected_submission_name}"
        )

    @property
    def problem(self) -> Problem[ProbInputType, ProbOutputType]:
        """The problem to be tested."""
        return self._problem

    @problem.setter
    def problem(self, prob: Problem) -> None:
        """Set the problem to be tested."""
        self._problem = prob

    @property
    def submission(self) -> Any | None:
        """The submission to be tested against."""
        return self._submission

    @property
    def submission_context(self) -> ContextManager:
        """The context of captured from the submission."""
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
        """Load the submission from a path.

        :param path: The path to load the submission from. If the path is a directory, it will be searched recursively.
        :raises NoSubmissionError: If no submission is found.
        :raises MultipleSubmissionError: If multiple submissions are found.
        """
        if self.problem.config.is_script:
            self._logger.debug("Loading script submission")
            submission_list = list(self._load_script_submission_from_path(path))
        else:
            self._logger.debug("Loading object submission")
            submission_list = list(self._load_object_submission_from_path(path))

        self._logger.debug(
            f"Found {len(submission_list)} submissions: {submission_list}"
        )

        if len(submission_list) == 0:
            raise NoSubmissionError(self.problem.expected_submission_name)
        elif len(submission_list) > 1:
            raise MultipleSubmissionError(self.problem.expected_submission_name)

        self._submission = submission_list[0]
        self._logger.debug("Submission loaded")

        return self

    def load_context_from_module(self, md: ModuleType) -> Self:
        """Load the context from a module.

        :param md: The module to load the context from.
        :raises MultipleContextValueError: If multiple context values are found.
        """
        for context_value_name in self.problem.config.captured_context:
            try:
                context_value = self._load_symbol_from_module(md, context_value_name)
            except AttributeError:
                continue

            if context_value_name in self.submission_context:
                raise MultipleContextValueError(context_value_name)

            self.submission_context[context_value_name] = context_value
            self._logger.debug(
                f"Loaded context value for {context_value_name} from {md}"
            )

        return self

    def check_context_completeness(self) -> None:
        """Check if the context is complete against what's required in the problem."""
        for context_value_name in self.problem.config.captured_context:
            if context_value_name not in self.submission_context:
                raise MissingContextValueError(context_value_name)

        self._logger.debug("Context completeness check passed")

    def run(
        self, metadata: GradescopeSubmissionMetadata | None = None
    ) -> List[TestResult]:
        """Run the tests.

        :param metadata: The metadata of the submission, which could be None.
        """
        if self.problem is None:
            raise InternalError("No problem loaded.")

        if self.submission is None:
            raise InternalError("No submission loaded.")

        self.check_context_completeness()

        test_results: List[TestResult] = []

        for test in self.problem.generate_tests():
            self._logger.debug(f"Running test {test.test_param.format()}")

            test_results.append(
                test.load_metadata(metadata)
                .load_context(self.submission_context)
                .run_test(
                    deepcopy(self.submission),
                    TestResult(default_name=test.test_param.format()),
                )
            )

        self.run_post_tests(results=test_results, metadata=metadata)

        return test_results

    def run_post_tests(
        self,
        *,
        results: List[TestResult],
        metadata: GradescopeSubmissionMetadata | None,
    ) -> List[TestResult]:
        """Run the post tests.

        :param results: The results of the tests.
        :param metadata: The metadata of the submission, which could be None.
        """
        addition_test_results = []
        for post_test_case in self.problem.post_tests:
            if post_test_case.as_test_case:
                result_proxy = TestResult(post_test_case.post_test_fn.__name__)
            else:
                result_proxy = None

            self._logger.debug(f"Running post test {post_test_case}")
            post_test_case.post_test_fn(results, result_proxy, metadata)
            self._logger.debug(f"Post test {post_test_case} completed")

            if result_proxy is not None:
                addition_test_results.append(result_proxy)

        results.extend(addition_test_results)
        self._logger.debug("Post tests completed and results added")

        return results

    @classmethod
    def from_file(cls, path: Path) -> Tester:
        """Load a tester from a file.

        :param path: The path to load the tester from.
        """
        with open(path, "rb") as f:
            tester = ProblemUnpickler(f).load()

        _tester_logger.debug(f"Tester loaded from path {path.absolute()}")

        return tester

    def dump_to(self, path: Path | str) -> None:
        """Dump the tester to a file.

        :param path: The path to dump the tester to.
        """
        with open(path, "wb") as f:
            dump(self, f)

        _tester_logger.debug(f"Tester dumped to path {path.absolute()}")
