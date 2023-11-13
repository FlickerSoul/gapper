from __future__ import annotations

from typing import List

from gapper.core.errors import (
    InternalError,
    SubmissionSyntaxError,
    TestFailedError,
)
from gapper.core.problem import Problem
from gapper.core.test_result import TestResult
from gapper.core.utils import PostTestFn
from gapper.gradescope.datatypes.gradescope_meta import (
    GradescopeSubmissionMetadata,
)


class PostTest:
    """A decorator for post tests. Will be used as @post_test() decorator."""

    def __init__(self, post_test_fn: PostTestFn, as_test_case: bool = True) -> None:
        """A decorator for specifying post tests. Will be used as @post_test().

            from gapper import post_test, problem

            @post_test()
            @problem()
            ...

        :param post_test_fn: The function to be called after all tests are run.
        :param as_test_case: Whether to treat the post test as a test case.
            If this is set to True, the post test will incur a TestResult instance to be created
            and be added to the pool of all test results after the post testing phrase is completed.
            The test result will then be used to synthesize the score.

            If this is set to False, the post test will not incur a TestResult instance.
        """
        self.post_test_fn = post_test_fn
        self.as_test_case = as_test_case

    def __call__(self, problem: Problem) -> Problem:
        """Add the post test to the problem.

        :param problem: The problem to add the post test to.
        """
        problem.add_post_test(self)
        return problem

    def __repr__(self) -> str:
        return f"PostTest(post_test_fn={self.post_test_fn}, as_test_case={self.as_test_case})"

    def run(
        self,
        test_results: List[TestResult],
        result_proxy: TestResult | None,
        metadata: GradescopeSubmissionMetadata | None,
    ) -> TestResult | None:
        """Run the post test.

        :param test_results: The results of the tests.
        :param result_proxy: The proxy of the post test result.
        :param metadata: The metadata of the submission, which could be None.
        """

        try:
            self._run(test_results, result_proxy, metadata)
        except AssertionError as e:
            result_proxy and result_proxy.add_error(
                TestFailedError(e), set_failed=result_proxy.is_pass_status_unset
            )
        except SyntaxError as e:
            result_proxy and result_proxy.add_error(
                SubmissionSyntaxError(e),
                set_failed=result_proxy.is_pass_status_unset,
            )
        except Exception as e:
            result_proxy.add_error(
                InternalError(e), set_failed=result_proxy.is_pass_status_unset
            )
        else:
            if result_proxy and result_proxy.is_pass_status_unset:
                result_proxy.set_pass_status("passed")

        return result_proxy

    def _run(
        self,
        test_results: List[TestResult],
        result_proxy: TestResult,
        metadata: GradescopeSubmissionMetadata | None,
    ) -> None:
        self.post_test_fn(test_results, result_proxy, metadata)


post_test = PostTest
