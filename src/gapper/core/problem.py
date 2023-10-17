from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import (
    Callable,
    Generic,
    ParamSpec,
    TypeVar,
    Optional,
    Iterable,
    overload,
    TYPE_CHECKING,
    List,
    Generator,
)

from gapper.core.errors import MultipleProblemsDefinedError, NoProblemDefinedError
from gapper.core.unittest_wrapper import TestCaseWrapper
from gapper.core.utils import ModuleLoader

if TYPE_CHECKING:
    from gapper.core.test_parameter import TestParam

ProbInputType = ParamSpec("ProbInputType")
ProbOutputType = TypeVar("ProbOutputType")


@dataclass
class ProblemConfig:
    check_stdout: bool = False
    mock_input: bool = False
    captured_context: Iterable[str] = ()
    is_script: bool = False


class Problem(ModuleLoader, Generic[ProbInputType, ProbOutputType]):
    def __init__(
        self,
        solution: Callable[ProbInputType, ProbOutputType],
        *,
        config: ProblemConfig,
    ) -> None:
        self._config: ProblemConfig = config
        self._solution = solution
        self._test_params: List[TestParam] = []

    @property
    def config(self) -> ProblemConfig:
        return self._config

    @property
    def test_cases(self) -> List[TestParam]:
        return self._test_params

    @property
    def solution(self) -> Callable[ProbInputType, ProbOutputType]:
        return self._solution

    @property
    def expected_submission_name(self) -> str:
        return self.solution.__name__

    def add_test_parameter(self, test_param: TestParam) -> None:
        self._test_params.append(test_param)

    def __call__(
        self, *args: ProbInputType.args, **kwargs: ProbInputType.kwargs
    ) -> ProbOutputType:
        return self._solution(*args, **kwargs)

    def generate_tests(self) -> Generator[TestCaseWrapper, None, None]:
        yield from (TestCaseWrapper(param, self) for param in self._test_params)

    @classmethod
    def _search_problem(cls, path: Path) -> Generator[Problem, None, None]:
        if path.is_dir():
            if path.name == "__pycache__":
                return

            for sub_path in path.iterdir():
                yield from cls._search_problem(sub_path)
        else:
            if path.suffix != ".py":
                return

            spec, mod = cls._load_module_spec_and_module(path, exec_mod=True)

            for val in mod.__dict__.values():
                if isinstance(val, Problem):
                    yield val

    @classmethod
    def from_path(cls, path: Path) -> Problem:
        problems = list(cls._search_problem(path))

        if len(problems) == 0:
            raise NoProblemDefinedError()

        if len(problems) > 1:
            raise MultipleProblemsDefinedError(
                prob.expected_submission_name for prob in problems
            )

        return problems[0]


@overload
def problem(
    *, is_script: bool = False, context: Iterable[str] = ()
) -> Callable[
    [Callable[ProbInputType, ProbOutputType]], Problem[ProbInputType, ProbOutputType]
]:
    """Assert that this problem is a script."""
    ...


@overload
def problem(
    *, check_stdout: bool = False, mock_input: bool = False, context: Iterable[str] = ()
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
) -> Callable[
    [Callable[ProbInputType, ProbOutputType]], Problem[ProbInputType, ProbOutputType]
]:
    """Create a problem object."""

    if is_script:
        if check_stdout is not None or mock_input is not None:
            raise ValueError("Cannot specify check_stdout or mock_input for a script.")

        config = ProblemConfig(True, True)

    else:
        check_stdout = bool(check_stdout) or False
        mock_input = bool(mock_input) or False

        config = ProblemConfig(check_stdout, mock_input)

    config.captured_context = context
    config.is_script = is_script

    def _wrapper(
        fn: Callable[ProbInputType, ProbOutputType]
    ) -> Problem[ProbInputType, ProbOutputType]:
        return Problem(fn, config=config)

    return _wrapper
