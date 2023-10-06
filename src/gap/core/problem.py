from dataclasses import dataclass
from typing import Callable, Generic, ParamSpec, TypeVar, Optional, Iterable, overload

ProbInputType = ParamSpec("ProbInputType")
ProbOutputType = TypeVar("ProbOutputType")


@dataclass
class ProblemConfig:
    pass


class Problem(Generic[ProbInputType, ProbOutputType]):
    pass


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

    def _wrapper(
        fn: Callable[ProbInputType, ProbOutputType]
    ) -> Problem[ProbInputType, ProbOutputType]:
        return Problem()

    return _wrapper
