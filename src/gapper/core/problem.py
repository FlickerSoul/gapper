"""This module defines the Problem class, which is the abstract representation of a assignment problem."""
from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Callable,
    Generator,
    Generic,
    Iterable,
    List,
    Optional,
    ParamSpec,
    TypedDict,
    TypeVar,
    overload,
)

from gapper.core.errors import MultipleProblemsDefinedError, NoProblemDefinedError
from gapper.core.unittest_wrapper import TestCaseWrapper
from gapper.core.utils import ModuleLoader

if TYPE_CHECKING:
    from gapper.core.test_parameter import TestParam
    from gapper.core.tester import PostTest

ProbInputType = ParamSpec("ProbInputType")
ProbOutputType = TypeVar("ProbOutputType")

_problem_logger = logging.getLogger("gapper.problem")


@dataclass(frozen=True)
class GSConnectConfig:
    cid: str
    aid: str


class ProblemConfigExtra(TypedDict):
    gs_connect: Optional[GSConnectConfig]


@dataclass
class ProblemConfig:
    """Problem configuration.

    :param check_stdout: Whether to check the stdout of the solution.
    :param mock_input: Whether to mock the input of the solution.
    :param captured_context: The context to capture from the submission.
    :param is_script: Whether this problem is a script.
    :param easy_context: Whether to use context directly in gap override tests.
    """

    check_stdout: bool = False
    mock_input: bool = False
    captured_context: Iterable[str] = ()
    easy_context: bool = False
    is_script: bool = False
    extras: ProblemConfigExtra = field(default_factory=lambda: defaultdict(None))


class Problem(ModuleLoader, Generic[ProbInputType, ProbOutputType]):
    """A abstract representation of a assignment problem."""

    def __init__(
        self,
        solution: Callable[ProbInputType, ProbOutputType],
        *,
        config: ProblemConfig,
    ) -> None:
        """Create a problem object.

        :param solution: The solution to the problem.
        :param config: The configuration of the problem.
        """
        self._config: ProblemConfig = config
        self._solution = solution
        self._test_params: List[TestParam] = []
        self._post_tests: List[PostTest] = []
        self._logger = _problem_logger.getChild(self.expected_submission_name)

        self._logger.debug(f"Problem created with config: {self._config}")

    @property
    def config(self) -> ProblemConfig:
        """The configuration of the problem."""
        return self._config

    @property
    def test_cases(self) -> List[TestParam]:
        """The test cases of the problem."""
        return self._test_params

    @property
    def solution(self) -> Callable[ProbInputType, ProbOutputType]:
        """The solution to the problem."""
        return self._solution

    @property
    def post_tests(self) -> List[PostTest]:
        """The post tests of the problem."""
        return self._post_tests

    @property
    def expected_submission_name(self) -> str:
        """The expected name of the submission."""
        return getattr(self.solution, "__name__", None) or "<unnamed_submission>"

    def add_test_parameter(self, test_param: TestParam) -> None:
        """Add a test parameter to the problem.

        :param test_param: The test parameter to add.
        """
        self._logger.debug(f"Adding test parameter {test_param.format()}")
        self._test_params.append(test_param)

    def add_post_test(self, post_test: PostTest) -> None:
        """Add a post test to the problem.

        :param post_test: The post test to add.
        """
        self._logger.debug(f"Adding post test {post_test}")
        self._post_tests.append(post_test)

    def __call__(
        self, *args: ProbInputType.args, **kwargs: ProbInputType.kwargs
    ) -> ProbOutputType:
        return self._solution(*args, **kwargs)

    def generate_tests(self) -> Generator[TestCaseWrapper, None, None]:
        """Generate the test cases."""
        yield from (TestCaseWrapper(param, self) for param in self._test_params)

    @classmethod
    def _search_problem(cls, path: Path) -> Generator[Problem, None, None]:
        if path.is_dir():
            if path.name == "__pycache__":
                _problem_logger.debug("Skipping __pycache__ directory")
                return

            for sub_path in path.iterdir():
                yield from cls._search_problem(sub_path)
        else:
            if path.suffix != ".py":
                _problem_logger.warning(
                    f"Skipping {path.absolute()} as it is not a python file"
                )
                return

            spec, mod = cls._load_module_spec_and_module(path, exec_mod=True)

            for val in mod.__dict__.values():
                if isinstance(val, Problem):
                    _problem_logger.debug(f"Found problem {val} in {path.absolute()}")
                    yield val

    @classmethod
    def from_path(cls, path: Path) -> Problem:
        """Load a problem from a path.

        :param path: The path to load the problem from. If the path is a directory, it will be searched recursively.
                     But only one problem can be defined in a directory.
        """
        problems = list(cls._search_problem(path))
        _problem_logger.debug(f"Found {len(problems)} problems in {path}")

        if len(problems) == 0:
            raise NoProblemDefinedError()

        if len(problems) > 1:
            raise MultipleProblemsDefinedError(
                prob.expected_submission_name for prob in problems
            )

        return problems[0]


@overload
def problem(
    *, is_script: bool = False, context: Iterable[str] = (), easy_context: bool = False
) -> Callable[
    [Callable[ProbInputType, ProbOutputType]], Problem[ProbInputType, ProbOutputType]
]:
    """Assert that this problem is a script."""
    ...


@overload
def problem(
    *,
    check_stdout: bool = False,
    mock_input: bool = False,
    context: Iterable[str] = (),
    easy_context: bool = False,
) -> Callable[
    [Callable[ProbInputType, ProbOutputType]], Problem[ProbInputType, ProbOutputType]
]:
    """Assert that this problem will be tested with custom input & captured stdout."""
    ...


def problem(
    *,
    is_script: bool = False,
    check_stdout: Optional[bool] = None,
    mock_input: Optional[bool] = None,
    context: Iterable[str] = (),
    easy_context: bool = False,
) -> Callable[
    [Callable[ProbInputType, ProbOutputType]], Problem[ProbInputType, ProbOutputType]
]:
    """Create a problem object.

    :param is_script: Whether this problem is a script. This cannot coexist with check_stdout or mock_input.
    :param check_stdout: Whether to check the stdout of the solution.
    :param mock_input: Whether to mock the input of the solution.
    :param context: The context to capture from the submission.
    :param easy_context: Whether to use context directly in gap override tests.
    """

    if is_script:
        if check_stdout is not None or mock_input is not None:
            raise ValueError("Cannot specify check_stdout or mock_input for a script.")

        check_stdout, mock_input = True, True

    else:
        check_stdout = bool(check_stdout) or False
        mock_input = bool(mock_input) or False

    config = ProblemConfig(
        check_stdout=check_stdout,
        mock_input=mock_input,
        captured_context=context,
        is_script=is_script,
        easy_context=easy_context,
    )

    def _wrapper(
        fn: Callable[ProbInputType, ProbOutputType]
    ) -> Problem[ProbInputType, ProbOutputType]:
        return Problem(fn, config=config)

    return _wrapper
