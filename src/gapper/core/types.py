from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, NamedTuple, Protocol

if TYPE_CHECKING:
    from gapper.core.test_result import TestResult
    from gapper.core.unittest_wrapper import TestCaseWrapper
    from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata


@dataclass
class CustomTestData[T]:
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
class PreTestHookData[T](HookDataBase):
    case: TestCaseWrapper
    result_proxy: TestResult
    solution: T
    submission: T


@dataclass
class PostTestHookData[T](HookDataBase):
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

    def __call__[T](self, data: PreTestHookData[T]) -> None:
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

    def __call__[T](self, data: PostTestHookData[T]) -> None:
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
