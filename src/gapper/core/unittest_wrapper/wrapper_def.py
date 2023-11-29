"""TestCaseWrapper and related helper definitions."""
from __future__ import annotations

import logging
from copy import deepcopy
from types import FunctionType
from typing import (
    TYPE_CHECKING,
    Any,
    Self,
    Sequence,
    Tuple,
)
from unittest import TestCase
from unittest.mock import patch

from gapper.core.errors import (
    InternalError,
    SubmissionSyntaxError,
    TestFailedError,
)
from gapper.core.hook import HookHolder
from gapper.core.pipeline_support import PipelineBase
from gapper.core.test_result import TestResult
from gapper.core.tester import HookTypes
from gapper.core.types import (
    CustomEqualityCheckFn,
    CustomTestData,
    CustomTestFn,
    PostHookData,
    PreHookData,
    ResultBundle,
)
from gapper.core.unittest_wrapper.utils import ContextManager, EvalFn, stdout_cm_adder
from gapper.core.unittest_wrapper.wrapper_hooks import PostHook, PreHook
from gapper.core.utils import (
    apply_context_on_fn,
    generate_custom_input,
)

if TYPE_CHECKING:
    from gapper.core.problem import Problem
    from gapper.core.test_parameter import TestParam
    from gapper.gradescope.datatypes.gradescope_meta import (
        GradescopeSubmissionMetadata,
    )

_test_wrapper_logger = logging.getLogger("gapper.test_wrapper")


class TestCaseWrapper(TestCase, HookHolder):
    """A wrapper for the unittest.TestCase class.

    This serves as a proxy for the testing process to get useful
    information about the test and functions for testing
    """

    def __init__(self, test_param: TestParam, problem: Problem) -> None:
        """Create a test case wrapper.

        :param test_param: The test parameter to be used in testing.
        :param problem: The problem definition to be used in testing.
        """
        TestCase.__init__(self)
        HookHolder.__init__(self)
        self._test_param = test_param
        self._problem = problem
        self._context: ContextManager | None = None
        self._metadata: GradescopeSubmissionMetadata | None = None
        self._logger = _test_wrapper_logger.getChild(self.test_param.format())

    @property
    def test_param(self) -> TestParam:
        """The test parameter to be used in testing."""
        return self._test_param

    @property
    def problem(self) -> Problem:
        """The problem definition to be used in testing."""
        return self._problem

    @property
    def context(self) -> ContextManager | None:
        """The context of the submission."""
        return self._context

    @property
    def metadata(self) -> GradescopeSubmissionMetadata | None:
        """The metadata of the submission."""
        return self._metadata

    @stdout_cm_adder
    def _eval_regular[Input](self, to_be_eval: Input, param: TestParam) -> Any:
        return to_be_eval(*deepcopy(param.args), **deepcopy(param.kwargs))

    @stdout_cm_adder
    def _eval_mock_input[Input](self, to_be_eval: Input, param: TestParam) -> Any:
        """Evaluate the function with mock input."""
        with patch("builtins.input", generate_custom_input(deepcopy(param.args))):
            result = to_be_eval()

        return result

    @stdout_cm_adder
    def _eval_pipeline[Input](self, to_be_eval: Input, param: TestParam) -> Any:
        """Evaluate the pipeline."""
        result = []
        for i, pipeline_entry in enumerate(param.args):
            if not isinstance(pipeline_entry, PipelineBase):
                raise InternalError(f"The {i}th pipeline entry is not a PipelineBase.")

            if pipeline_entry.replace:
                to_be_eval = pipeline_entry(to_be_eval)
                result.append(None)
            else:
                result.append(pipeline_entry(to_be_eval))

        return result

    def _select_eval_fn(self) -> EvalFn:
        """Select the eval function based on the test parameter."""
        if self.problem.config.mock_input:
            return self._eval_mock_input
        elif self.test_param.param_info.gap_is_pipeline:
            return self._eval_pipeline
        else:
            return self._eval_regular

    def run_test(self, submission: Any, result: TestResult) -> TestResult:
        """Run the test on the submission.

        :param submission: The submission to be tested.
        :param result: The result object to be used and written to.
        :return: The result object passed to this method.
        """
        self._setup_test_result(result)

        try:
            self._run_test(submission, result)
        except AssertionError as e:
            result.add_error(TestFailedError(e), set_failed=result.is_pass_status_unset)
        except SyntaxError as e:
            result.add_error(
                SubmissionSyntaxError(e), set_failed=result.is_pass_status_unset
            )
        except Exception as e:
            result.add_error(InternalError(e), set_failed=result.is_pass_status_unset)
        else:
            if result.is_pass_status_unset:
                result.set_pass_status("passed")

        return result

    def check_test(self) -> Tuple[bool, Any, str] | None:
        """Check if the test passes against the gap_expect and gap_expect_stdout.

        :return: True if the test passes, False if the test fails, None if the test is skipped.
        """
        self._logger.debug("Checking test")
        if (
            self.test_param.param_info.gap_expect is None
            and self.test_param.param_info.gap_expect_stdout is None
        ):
            self._logger.debug("Test skipped")
            return None

        if self.test_param.param_info.gap_override_test is not None:
            raise Warning("gap_override_test is not None, check_test is ignored.")
        else:
            if self.test_param.param_info.gap_override_check:
                check_fn: CustomEqualityCheckFn = (
                    self.test_param.param_info.gap_override_check
                )
            else:
                check_fn = self.assertEqual  # type: ignore

            self._logger.debug(f"Checking test equality with fn {check_fn.__name__}")

            eval_fn: EvalFn = self._select_eval_fn()

            self._logger.debug(f"Selected evaluation fn {eval_fn.__name__}")

            actual_result, actual_out = eval_fn(self.problem.solution, self.test_param)

            flag = True

            if self.test_param.param_info.gap_expect is not None:
                try:
                    check_fn(actual_result, self.test_param.param_info.gap_expect)
                except AssertionError:
                    self._logger.debug(
                        "Check failed because it does not meet gap_expect"
                    )
                    flag = False

            if self.test_param.param_info.gap_expect_stdout is not None:
                try:
                    assert actual_out == self.test_param.param_info.gap_expect_stdout
                except AssertionError:
                    self._logger.debug(
                        "Check failed because it does not meet gap_expect_stdout"
                    )
                    flag = False

            return flag, actual_result, actual_out

    def _setup_test_result(self, result: TestResult) -> None:
        """Set the test result object to default values specified in the info."""
        result.set_name(self.test_param.param_info.gap_name)
        result.set_extra_points(self.test_param.param_info.gap_extra_points)
        if (
            self.test_param.param_info.gap_max_score is None
            and self.test_param.param_info.gap_weight is None
        ):
            result.set_default_weight()
        else:
            result.set_max_score(self.test_param.param_info.gap_max_score)
            result.set_weight(self.test_param.param_info.gap_weight)
        result.set_hidden(self.test_param.param_info.gap_hidden)
        if self.test_param.param_info.gap_description is not None:
            result.add_description(
                *(
                    [self.test_param.param_info.gap_description]
                    if isinstance(self.test_param.param_info.gap_description, str)
                    else self.test_param.param_info.gap_description
                )
            )

        self._logger.debug(f"Test result initialized: {result}")

    def generate_hooks(self, hook_type: HookTypes) -> None:
        match hook_type:
            case HookTypes.PRE_HOOK:
                hook_fns = self.test_param.param_info.gap_pre_hooks
                hook_wrapper = PreHook
            case HookTypes.POST_HOOK:
                hook_fns = self.test_param.param_info.gap_post_hooks
                hook_wrapper = PostHook
            case _:
                raise ValueError(f"Test Case cannot handle hook {hook_type}")

        if hook_fns is None:
            self._hooks[hook_type] = []
        else:
            if not isinstance(hook_fns, Sequence):
                hook_fns: Sequence = [hook_fns]

            self._hooks[hook_type] = [
                hook_wrapper(self.apply_context(hook_fn)) for hook_fn in hook_fns
            ]

        self._logger.debug(f"Generated {hook_type} hooks")

    def run_hooks(self, hook_type: HookTypes, data) -> None:
        self._logger.debug(f"Start running {hook_type} hooks")
        for hook in self.get_or_gen_hooks(hook_type):
            hook.run(data)
        self._logger.debug(f"Finished running {hook_type} hooks")

    def _run_test(self, submission: Any, result: TestResult) -> TestResult:
        """Run the test on the submission.

        :param submission: The submission to be tested.
        :param result: The result object to be used and written to.
        """
        self._logger.debug(f"Running test on submission {submission}")

        if self.test_param.param_info.gap_override_test is not None:
            self._logger.debug("Handing testing to gap_override_test")
            override_test: CustomTestFn = self.apply_context(
                self.test_param.param_info.gap_override_test
            )
            override_test(
                CustomTestData(self, result, self.problem.solution, submission)
            )
        else:
            eval_fn: EvalFn = self._select_eval_fn()
            self._logger.debug(f"Selected evaluation fn {eval_fn.__name__}")

            self.run_hooks(
                HookTypes.PRE_HOOK,
                PreHookData(self, result, self.problem.solution, submission),
            )

            self._logger.debug(f"Running test evaluation")
            expected = eval_fn(self.problem.solution, self.test_param)
            actual = eval_fn(submission, self.test_param)

            self.check_results(expected, actual)

            self.run_hooks(
                HookTypes.POST_HOOK,
                PostHookData(
                    self,
                    result,
                    self.problem.solution,
                    submission,
                    expected,
                    actual,
                ),
            )

            self.tear_down_hooks(HookTypes.PRE_HOOK)
            self.tear_down_hooks(HookTypes.POST_HOOK)

        self._logger.debug("Test completed")

        return result

    def check_results(self, expected: ResultBundle, actual: ResultBundle) -> None:
        if self.test_param.param_info.gap_override_check:
            check_fn: CustomEqualityCheckFn = (
                self.test_param.param_info.gap_override_check
            )
        else:
            check_fn = self.assertEqual  # type: ignore
        self._logger.debug(f"Checking test equality with fn {check_fn.__name__}")

        check_fn(expected.output, actual.output)
        if self.problem.config.check_stdout:
            check_fn(expected.stdout, actual.stdout)

        self._logger.debug("Test checked")

    def apply_context[T: FunctionType](self, fn: T) -> T:
        if (
            self.problem.config.easy_context
            or self.test_param.param_info.gap_easy_context
        ):
            self._logger.debug("Using easy context")
            return apply_context_on_fn(fn, self.context)
        else:
            return fn

    def load_context(self, context: ContextManager) -> Self:
        """Load the submission context into the test case.

        :param context: The context to load.
        """
        self._context = deepcopy(context)
        self._logger.debug(f"Context loaded: {self._context}")
        return self

    def load_metadata(self, metadata: GradescopeSubmissionMetadata | None) -> Self:
        """Load the submission metadata into the test case.

        :param metadata: The metadata to load. The metadata could be None.
        """
        self._metadata = metadata
        self._logger.debug(f"Metadata loaded: {self._metadata}")
        return self
