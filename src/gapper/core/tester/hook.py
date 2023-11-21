from __future__ import annotations

import abc
import enum
from typing import TYPE_CHECKING, Callable, ClassVar

from gapper.core.errors import InternalError, SubmissionSyntaxError, TestFailedError
from gapper.core.test_parameter import ParamExtractor
from gapper.core.test_result import TestResult
from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata

if TYPE_CHECKING:
    from gapper.core.problem import Problem


class HookTypes(enum.Enum):
    """The types of hooks."""

    PRE_TEST = "pre_test"
    POST_TEST = "post_test"


class HookBase[FnType: Callable[..., None]](ParamExtractor):
    _hook_type: ClassVar[HookTypes]

    def __init__(
        self,
        hook_fn: FnType,
        as_test_case: bool = True,
        **kwargs,
    ) -> None:
        """
        :param hook_fn: The function when the hook is triggered.
        :param as_test_case: Whether to treat the post test as a test case.
            If this is set to True, this hook will incur a TestResult instance to be
            created and will then be used to synthesize the score. Therefore, it will
            also be seen as an entry in gradescope.

            If this is set to False, it will only have side effects and will not be seen
            as an entry in gradescope.
        :param kwargs: gap keyword parameters.
        """
        super().__init__(kwargs)

        self.hook_fn = hook_fn
        self.as_test_case = as_test_case

    def __call__(self, problem: Problem) -> Problem:
        """Add the post test to the problem.

        :param problem: The problem to add the post test to.
        """
        problem.add_hook(self, self._hook_type)
        return problem

    def run(
        self,
        *args,
        result_proxy: TestResult | None,
        metadata: GradescopeSubmissionMetadata | None,
        **kwargs,
    ) -> TestResult | None:
        self._setup_result(result_proxy)

        try:
            self._run(*args, result_proxy=result_proxy, metadata=metadata, **kwargs)
        except AssertionError as e:
            result_proxy.add_error(
                TestFailedError(e), set_failed=result_proxy.is_pass_status_unset
            )
        except SyntaxError as e:
            result_proxy.add_error(
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

    def _setup_result(self, result: TestResult | None) -> None:
        if result is None:
            return

        result.set_name(self.param_info.gap_name)
        result.set_extra_points(self.param_info.gap_extra_points)
        if self.param_info.gap_max_score is None and self.param_info.gap_weight is None:
            result.set_default_weight()
        else:
            result.set_max_score(self.param_info.gap_max_score)
            result.set_weight(self.param_info.gap_weight)
        result.set_hidden(self.param_info.gap_hidden)
        if self.param_info.gap_description is not None:
            result.add_description(
                *(
                    [self.param_info.gap_description]
                    if isinstance(self.param_info.gap_description, str)
                    else self.param_info.gap_description
                )
            )

    @abc.abstractmethod
    def _run(
        self,
        *args,
        result_proxy: TestResult | None,
        metadata: GradescopeSubmissionMetadata | None,
        **kwargs,
    ) -> None:
        ...

    @abc.abstractmethod
    def __repr__(self) -> str:
        ...
