from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, NamedTuple, Protocol, Tuple

if TYPE_CHECKING:
    from gapper.core.test_parameter import TestParam
    from gapper.core.test_result import TestResult
    from gapper.core.unittest_wrapper import TestCaseWrapper
    from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata


class _TCMixin(Protocol):
    """The mixin for test case."""

    case: TestCaseWrapper

    @property
    def tc(self) -> TestCaseWrapper:
        """The test case wrapper."""
        return self.case

    @property
    def param(self) -> TestParam:
        """The parameter information of the test case."""
        return self.case.test_param

    @property
    def args(self) -> Tuple[Any, ...]:
        """The arguments of the test case."""
        return self.case.test_param.args

    @property
    def kwargs(self) -> Dict[str, Any]:
        """The keyword arguments of the test case."""
        return self.case.test_param.kwargs


class _SolSubMixin[T](Protocol):
    solution: T
    submission: T

    @property
    def sol(self) -> T:
        """The solution object."""
        return self.solution

    @property
    def sub(self) -> T:
        """The submission object."""
        return self.submission


class _SolSubResultMixin[T](Protocol):
    expected_results: ResultBundle
    actual_results: ResultBundle

    @property
    def sol_output(self) -> T:
        """The solution output."""
        return self.expected_results.output

    @property
    def sol_stdout(self) -> str | None:
        """The solution stdout."""
        return self.expected_results.stdout

    @property
    def sub_output(self) -> T:
        """The submission output."""
        return self.actual_results.output

    @property
    def sub_stdout(self) -> str | None:
        """The submission stdout."""
        return self.actual_results.stdout


@dataclass
class CustomTestData[T](_TCMixin, _SolSubMixin[T]):
    case: TestCaseWrapper
    result_proxy: TestResult
    solution: T
    submission: T


@dataclass
class CustomEqualityTestData[T]:
    expected: T
    actual: T
    msg: str | None = field(default=None)


class HookDataBase(Protocol):
    result_proxy: TestResult | None


@dataclass
class PreHookData[T](HookDataBase, _TCMixin, _SolSubMixin[T]):
    case: TestCaseWrapper
    result_proxy: TestResult
    solution: T
    submission: T


@dataclass
class PostHookData[T](HookDataBase, _TCMixin, _SolSubMixin[T], _SolSubResultMixin[T]):
    case: TestCaseWrapper
    result_proxy: TestResult
    solution: T
    submission: T
    expected_results: ResultBundle
    actual_results: ResultBundle


@dataclass
class PreTestsData[T](HookDataBase):
    result_proxy: TestResult | None = field(default=None)
    metadata: GradescopeSubmissionMetadata | None = field(default=None)


@dataclass
class PostTestsData[T](HookDataBase):
    test_results: List[TestResult]
    result_proxy: TestResult | None = field(default=None)
    metadata: GradescopeSubmissionMetadata | None = field(default=None)


class CustomTestFn(Protocol):
    """The function type to be called for custom tests."""

    def __call__[T](self, data: CustomTestData[T]) -> None:
        """Implement.

        :param data: The CustomTestData instance.
        :raises AssertionError: It should raise assertion error if test fails.
        """
        ...


class CustomEqualityCheckFn(Protocol):
    """The function type to be called for custom equality checks."""

    def __call__[T](self, data: CustomEqualityTestData[T]) -> None:
        """Implement.

        :param data: The CustomEqualityTestData instance.
        :raises AssertionError: It should raise assertion error if the equality check tails
        """
        ...


class PreHookFn(Protocol):
    """The function type to be called for post checks all the equality check of a test case."""

    def __call__[T](self, data: PreHookData[T]) -> None:
        """Implement.

        :param data: The PreTestHookData instance.
        :raises AssertionError: It should raise assertion error if the pre hook fails.
        """
        ...


class ResultBundle[Output](NamedTuple):
    output: Output
    stdout: str | None


class PostHookFn(Protocol):
    """The function type to be called for post checks all the equality check of a test case."""

    def __call__[T](self, data: PostHookData[T]) -> None:
        """Implement.

        :param data: The PostTestHookData instance.
        :raises AssertionError: It should raise assertion error if the post hook fails.
        """
        ...


class PreTestsFn(Protocol):
    def __call__(self, data: PreTestsData) -> None:
        """Implement.

        :param data: The PreTestsData instance.
        :raises AssertionError: It should raise assertion error if the pre tests hook fail.
        """


class PostTestsFn(Protocol):
    """The function type to be called after all tests are run."""

    def __call__(self, data: PostTestsData) -> None:
        """Implement.

        :param data: The PostTestsData instance.
        :raises AssertionError: It should raise assertion error if the post tests hook fail.
        """
        ...
