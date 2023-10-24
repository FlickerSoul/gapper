from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any, Callable, NamedTuple, Protocol, Self
from unittest import TestCase
from unittest.mock import patch

from gapper.core.errors import (InternalError, SubmissionSyntaxError,
                                TestFailedError)
from gapper.core.pipeline_support import PipelineBase
from gapper.core.test_result import TestResult
from gapper.core.utils import CaptureStdout, generate_custom_input

if TYPE_CHECKING:
    from gapper.core.problem import Problem
    from gapper.core.test_parameter import TestParam
    from gapper.core.utils import CustomEqualityCheckFn
    from gapper.gradescope.datatypes.gradescope_meta import \
        GradescopeSubmissionMetadata


class ContextManager(dict):
    def __getattr__(self, item: str) -> Any:
        try:
            return self[item]
        except KeyError as e:
            raise AttributeError from e


class EvalOutput[Output](NamedTuple):
    output: Output
    stdout: str | None


class EvalFn[Input, Output](Protocol):
    def __call__(self, to_be_eval: Input, param: TestParam) -> EvalOutput:
        ...


def _stdout_cm_adder[
    Output
](fn: Callable[..., Output]) -> Callable[..., EvalOutput[Output]]:
    def _wrapper(self, *args, **kwargs) -> Any:
        with CaptureStdout(capture=self.problem.config.check_stdout) as cm:
            res = fn(self, *args, **kwargs)

        return res, cm.value

    return _wrapper


class TestCaseWrapper(TestCase):
    def __init__(self, test_param: TestParam, problem: Problem) -> None:
        super().__init__()
        self._test_param = test_param
        self._problem = problem
        self._context: ContextManager | None = None
        self._metadata: GradescopeSubmissionMetadata | None = None

    @property
    def test_param(self) -> TestParam:
        return self._test_param

    @property
    def problem(self) -> Problem:
        return self._problem

    @property
    def context(self) -> ContextManager | None:
        return self._context

    @property
    def metadata(self) -> GradescopeSubmissionMetadata | None:
        return self._metadata

    @_stdout_cm_adder
    def _eval_regular[Input](self, to_be_eval: Input, param: TestParam) -> Any:
        return to_be_eval(*deepcopy(param.args), **deepcopy(param.kwargs))

    @_stdout_cm_adder
    def _eval_mock_input[Input](self, to_be_eval: Input, param: TestParam) -> Any:
        """Evaluate the function with mock input."""
        with patch("builtins.input", generate_custom_input(deepcopy(param.args))):
            result = to_be_eval()

        return result

    @_stdout_cm_adder
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

        :submission: The submission to be tested.
        :result: The result object to be used and written to.
        :return: The result object passed to this method.
        """
        self._set_test_result(result)

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

    def check_test(self) -> bool | None:
        """Check if the test passes.

        :return: True if the test passes, False if the test fails, None if the test is skipped.
        """
        if (
            not self.test_param.param_info.gap_expect
            and not self.test_param.param_info.gap_expect_stdout
        ):
            return

        if self.test_param.param_info.gap_override_test is not None:
            raise Warning("gap_override_test is not None, check_test is ignored.")
        else:
            if self.test_param.param_info.gap_override_check:
                check_fn: CustomEqualityCheckFn = (
                    self.test_param.param_info.gap_override_check
                )
            else:
                check_fn = self.assertEqual  # type: ignore

            eval_fn: EvalFn = self._select_eval_fn()

            actual_result, actual_out = eval_fn(self.problem.solution, self.test_param)

            flag = True

            if self.test_param.param_info.gap_expect is not None:
                try:
                    check_fn(actual_result, self.test_param.param_info.gap_expect)
                except AssertionError:
                    flag = False

            if self.test_param.param_info.gap_expect_stdout is not None:
                flag = flag & (
                    actual_out == self.test_param.param_info.gap_expect_stdout
                )

            return flag

    def _set_test_result(self, result: TestResult) -> None:
        """Set the test result object to default values specified in the info."""
        result.set_name(self.test_param.param_info.gap_name)
        result.set_extra_points(self.test_param.param_info.gap_extra_points)
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

    def _run_test(self, submission: Any, result: TestResult) -> TestResult:
        """Run the test on the submission."""

        if self.test_param.param_info.gap_override_test is not None:
            self.test_param.param_info.gap_override_test(
                self, result, self.problem.solution, submission
            )
        else:
            if self.test_param.param_info.gap_override_check:
                check_fn: CustomEqualityCheckFn = (
                    self.test_param.param_info.gap_override_check
                )
            else:
                check_fn = self.assertEqual  # type: ignore

            eval_fn: EvalFn = self._select_eval_fn()

            expected_result, expected_out = eval_fn(
                self.problem.solution, self.test_param
            )
            actual_result, actual_out = eval_fn(submission, self.test_param)

            check_fn(expected_result, actual_result)
            if self.problem.config.check_stdout:
                check_fn(expected_out, actual_out)

        return result

    def load_context(self, context: ContextManager) -> Self:
        """Load the context into the test case."""
        self._context = deepcopy(context)
        return self

    def load_metadata(self, metadata: GradescopeSubmissionMetadata | None) -> Self:
        """Load the metadata into the test case."""
        self._metadata = metadata
        return self
