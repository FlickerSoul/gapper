"""Utility functions and classes for the core module."""
from __future__ import annotations

import importlib.util
from contextlib import redirect_stdout
from importlib.machinery import ModuleSpec
from io import StringIO
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Iterable, List, Protocol, Self, Tuple

if TYPE_CHECKING:
    from gapper.core.test_result import TestResult
    from gapper.core.unittest_wrapper import TestCaseWrapper
    from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata


class CustomTestFn(Protocol):
    """The custom test function protocol."""

    def __call__[
        T
    ](
        self,
        param: TestCaseWrapper,
        result_proxy: TestResult,
        solution: T,
        submission: T,
    ) -> None:
        """The function type to be called for custom tests.

        :param param: The TestCaseWrapper instance.
            It contains the test case information, including the test case name, the test case
            parameters, etc.
        :param result_proxy: The TestResult instance of this custom test to be used as a proxy.
            You can use this proxy to affect the test result of this test case. See
            .. seealso:: :class:`gapper.core.test_result.TestResult` for more details.
        :param solution: The expected result, which will be the solution under the @problem decorator
        :param submission: The actual result, which will be the submission from the student
        :raises AssertionError: It should raise assertion error if test fails.
        """
        ...


class CustomEqualityCheckFn(Protocol):
    """The custom equality check function protocol."""

    def __call__[T](self, expected: T, actual: T, msg: str | None = None) -> None:
        """The function type to be called for custom equality checks.

        :param expected: The expected result, which will be executed result of the solution
        :param actual: The actual result, which will be the executed result of the submission
        :param msg: The message to be printed if the equality check fails.
        :raises AssertionError: It should raise assertion error if the equality check tails
        """
        ...


class PostChecksFn(Protocol):
    """The post check function protocol."""

    def __call__[
        T
    ](
        self,
        param: TestCaseWrapper,
        result_proxy: TestResult,
        solution: T,
        submission: T,
        expected_results: Tuple[Any, str | None],
        actual_results: Tuple[Any, str | None],
    ) -> None:
        """The function type to be called for post checks all the equality check of a test case.

        :param param: The TestCaseWrapper instance.
            It contains the test case information, including the test case name, the test case
            parameters, etc.
        :param result_proxy: The TestResult instance of this custom test to be used as a proxy.
            You can use this proxy to affect the test result of this test case. See
            .. seealso:: :class:`gapper.core.test_result.TestResult` for more details.
        :param solution: The expected result, which will be the solution under the @problem decorator
        :param submission: The actual result, which will be the submission from the student
        :param expected_results: The expected results of the test case.
            It is a tuple of expected execution result and expected stdout result.
        :param actual_results: The actual results of the test case.
            It is a tuple of actual execution result and actual stdout result.
        :raises AssertionError: It should raise assertion error if the post check fails.
        """
        ...


class PostTestFn(Protocol):
    def __call__(
        self,
        results: List[TestResult],
        current_result_proxy: TestResult | None,
        metadata: GradescopeSubmissionMetadata | None,
    ) -> None:
        """The function type to be called after all tests are run.

        :param results: A list of test results from tested test cases.
            Note that, the number of results will remain the same through
            the post testing phrase, even though you have post tests with as_test_case
            set to True. The results from post tests will not be added until the
            post testing phrase is completed.
        :param current_result_proxy: The TestResult instance of this post test to be used as a proxy.
            If the post_test's as_test_case is set to False, this will be None.
        :param metadata: The metadata of the submission.
        """
        ...


def generate_custom_input(input_list: Iterable[str]) -> Callable[[Any], str]:
    """Generate a custom input function for a test case.

    :param input_list: The list of inputs to be used.
    """
    _iterator = iter(input_list)

    def _custom_input(*args: Any) -> str:
        """Mimic `input`'s behavior.

        Read a string from standard input.  The trailing newline is stripped.

        The prompt string, if given, is printed to standard output without a
        trailing newline before reading input.

        If the user hits EOF (*nix: Ctrl-D, Windows: Ctrl-Z+Return), raise EOFError.
        On *nix systems, readline is used if available.
        """
        print(*(str(arg) for arg in args), end="")
        return next(_iterator).rstrip("\n")

    return _custom_input


class CaptureStdout:
    """A context manager to capture stdout."""

    def __init__(self, capture: bool) -> None:
        """Create a context manager to capture stdout.

        :param capture: Whether to capture stdout.
        """
        self._capture: bool = capture
        self._capture_device: redirect_stdout[StringIO] | None = None
        self._io_device: StringIO | None = None

    def __enter__(self) -> Self:
        if self._capture:
            self._io_device = StringIO()
            self._capture_device = redirect_stdout(self._io_device)
            self._capture_device.__enter__()
        return self

    def __exit__(self, *args) -> None:
        if self._capture and self._capture_device:
            return self._capture_device.__exit__(*args)
        return None

    @property
    def value(self) -> str | None:
        """The captured stdout."""
        if self._capture and self._io_device:
            return self._io_device.getvalue()
        else:
            return None


class ModuleLoader:
    """A mixin class to load modules from files."""

    @staticmethod
    def _load_module_spec_and_module(
        path: Path, name: str = "module", exec_mod: bool = False
    ) -> Tuple[ModuleSpec, ModuleType]:
        spec = importlib.util.spec_from_file_location(name, path)

        if spec is None:
            # Based on inspection of the source, I'm not certain how this can happen, but my
            # type checker insists it can. This seems like the most reasonable error to
            # raise.
            raise FileNotFoundError(
                f"Cannot find module spec with path {path.absolute()}"
            )

        md = importlib.util.module_from_spec(spec)

        if exec_mod:
            spec.loader.exec_module(md)

        return spec, md

    @staticmethod
    def _load_symbol_from_module(md: ModuleType, symbol: str) -> Any:
        return getattr(md, symbol)
