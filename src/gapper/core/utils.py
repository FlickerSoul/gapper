"""Utility functions and classes for the core module."""
from __future__ import annotations

import importlib.util
import logging
from contextlib import redirect_stdout
from copy import copy
from functools import update_wrapper
from importlib.machinery import ModuleSpec
from io import StringIO
from pathlib import Path
from types import FunctionType, ModuleType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Protocol,
    Self,
    Tuple,
)

if TYPE_CHECKING:
    from gapper.core.test_result import TestResult
    from gapper.core.unittest_wrapper import TestCaseWrapper
    from gapper.gradescope.datatypes.gradescope_meta import (
        GradescopeSubmissionMetadata,
    )


_util_logger = logging.getLogger("gapper.core.utils")


class CustomTestFn(Protocol):
    """The function type to be called for custom tests."""

    def __call__[T](
        self,
        param: TestCaseWrapper,
        result_proxy: TestResult,
        solution: T,
        submission: T,
    ) -> None:
        """Implement.

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
    """The function type to be called for custom equality checks."""

    def __call__[T](self, expected: T, actual: T, msg: str | None = None) -> None:
        """Implement.

        :param expected: The expected result, which will be executed result of the solution
        :param actual: The actual result, which will be the executed result of the submission
        :param msg: The message to be printed if the equality check fails.
        :raises AssertionError: It should raise assertion error if the equality check tails
        """
        ...


class PreHookFn(Protocol):
    """The function type to be called for post checks all the equality check of a test case."""

    def __call__[T](
        self,
        param: TestCaseWrapper,
        result_proxy: TestResult,
        solution: T,
        submission: T,
    ) -> None:
        """Implement.

        :param param: The TestCaseWrapper instance.
            It contains the test case information, including the test case name, the test case
            parameters, etc.
        :param result_proxy: The TestResult instance of this custom test to be used as a proxy.
            You can use this proxy to affect the test result of this test case. See
            .. seealso:: :class:`gapper.core.test_result.TestResult` for more details.
        :param solution: The expected result, which will be the solution under the @problem decorator
        :param submission: The actual result, which will be the submission from the student
        :raises AssertionError: It should raise assertion error if the post check fails.
        """
        ...


class ResultBundle(NamedTuple):
    result: Any
    stdout: str | None


class PostHookFn(Protocol):
    """The function type to be called for post checks all the equality check of a test case."""

    def __call__[T](
        self,
        param: TestCaseWrapper,
        result_proxy: TestResult,
        solution: T,
        submission: T,
        expected_results: ResultBundle,
        actual_results: ResultBundle,
    ) -> None:
        """Implement.

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
    """The function type to be called after all tests are run."""

    def __call__(
        self,
        test_results: List[TestResult],
        test_proxy: TestResult | None,
        metadata: GradescopeSubmissionMetadata | None,
    ) -> None:
        """Implement.

        :param test_results: A list of test results from tested test cases.
            Note that, the number of results will remain the same through
            the post testing phrase, even though you have post tests with as_test_case
            set to True. The results from post tests will not be added until the
            post testing phrase is completed.
        :param test_proxy: The TestResult instance of this post test to be used as a proxy.
            If the post_test's as_test_case is set to False, this will be None.
        :param metadata: The metadata of the submission.
        """
        ...


def generate_custom_input(input_list: Iterable[str]) -> Callable[[Any], str]:
    """Generate a custom input function for a test case.

    :param input_list: The list of inputs to be used.
    :return: The custom input function.
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
        """Enter as a context manager."""
        if self._capture:
            self._io_device = StringIO()
            self._capture_device = redirect_stdout(self._io_device)
            self._capture_device.__enter__()
        return self

    def __exit__(self, *args) -> None:
        """Exit as the context manager."""
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
        """Load a module spec and module from a file.

        :param path: The path to the file.
        :param name: The name of the module to be registered.
        :param exec_mod: Whether to execute the module.
        :return: The module spec and the module.
        """
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
        """Load a symbol from a module."""
        return getattr(md, symbol)


def apply_context_on_fn[T: FunctionType](f: T, context: dict[str, Any]) -> T:
    """Apply a context on a function.

    :param f: The function to apply context on.
    :param context: The context to be applied.
    :return: The function with context applied.
    """
    if isinstance(f, FunctionType):
        _util_logger.debug(f"Applying context {context} on function {f}")

        # update closure with context
        _util_logger.debug("Gathering closure with context")
        closure_mod: Dict[str, int] = {}
        if f.__closure__ is not None:
            for context_var_name in context.keys():
                try:
                    closure_pos = f.__code__.co_freevars.index(context_var_name)
                    _util_logger.debug(
                        f"Found closure variable {context_var_name} at position {closure_pos}"
                    )
                    closure_mod[context_var_name] = closure_pos
                except ValueError:
                    _util_logger.debug(
                        f'Cannot find closure variable "{context_var_name}, skipped"'
                    )

        g = FunctionType(
            f.__code__,
            {
                **f.__globals__,
                **{
                    c_name: c_val
                    for c_name, c_val in context.items()
                    if c_name not in closure_mod
                },
            },  # copy globals and update with context
            name=f.__name__,
            argdefs=f.__defaults__,
            closure=f.__closure__,
        )
        g = update_wrapper(g, f)
        g.__kwdefaults__ = copy(f.__kwdefaults__)

        _util_logger.debug(f"Function {f} copied")

        for c_name, c_pos in closure_mod.items():
            _util_logger.debug(
                f"Updating closure variable {c_name} at position {c_pos}"
            )
            g.__closure__[c_pos].cell_contents = context[c_name]

        _util_logger.debug("Closure updated")

        return g
    else:
        raise TypeError(f"Cannot apply context on {f} because it is not a function")
