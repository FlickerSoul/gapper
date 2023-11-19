"""The Gradescope grading output JSON schema."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, List, Literal, Optional

from dataclasses_json import dataclass_json

from gapper.core.errors import InternalError, StudentError

if TYPE_CHECKING:
    from gapper.core.test_result import TestResult


VisibilityType = Literal["hidden", "after_due_date", "after_published", "visible"]
FormatType = Literal["text", "html", "simple_format", "md", "ansi"]
PassStateType = Literal["passed", "failed"]


@dataclass_json
@dataclass
class GradescopeTestJson:
    """The JSON schema for a single Test.

    :param score: The test's score. Required if no top-level score is set.
    :param max_score: The max score for the test.
    :param name: The test's name.
    :param output: Human-readable text output of the test.
    :param tags: Tags for the test.
    :param visibility: The test's visibility. "hidden", "visible", "after_due_date", "after_published"
    """

    score: Optional[float] = field(default=None)
    max_score: Optional[float] = field(default=None)
    status: Optional[PassStateType] = field(default=None)
    name: Optional[str] = field(default=None)
    name_format: FormatType = field(default="text")
    number: Optional[float] = field(default=None)
    output: Optional[str] = field(default=None)
    output_format: FormatType = field(default="text")
    tags: Optional[str] = field(default=None)
    visibility: VisibilityType = field(default="visible")

    @classmethod
    def from_test_result(cls, result: TestResult) -> GradescopeTestJson:
        """Convert a test result to Gradescope JSON.

        :param result: The test result to convert.
        :return: The Gradescope Test JSON.
        """
        if result.pass_status is None:
            # even though gradescope says status is optional, setting it to None
            # will cause an error.
            raise InternalError("pass_status of a test result cannot be None.")

        return cls(
            score=result.score,
            max_score=result.max_score,
            status=result.pass_status,
            name=result.rich_test_name,
            output=result.rich_test_output,
            visibility="hidden" if result.hidden else "visible",
        )


@dataclass_json
@dataclass
class GradescopeJson:
    """The JSON schema for Gradescope.

    We currently don't support the leaderboard and extra_data features of the gradescope
    schema. Those are documented on the autograder documentation, here:
    <https://gradescope-autograders.readthedocs.io/en/latest/specs/>.

    :param tests: The tests for the problem. Required if no global score provided.
    :param score: The overall score. Required if any test has no set score.
    :param execution_time: The execution time of all the tests, in seconds.
    :param output: The top-level, human-readable text output for all the problems.
    :param visibility: The default visibility for each test. Overridden by test-specific settings.
    :param stdout_visibility: Whether to show stdout for the tests. Same options as for visibility.
    """

    score: Optional[float] = None
    tests: list[GradescopeTestJson] = field(default_factory=list)
    execution_time: Optional[int] = None
    output: Optional[str] = None
    visibility: VisibilityType = "visible"
    stdout_visibility: Optional[str] = None

    @classmethod
    def from_test_results(
        cls,
        results: List[TestResult],
        score: float,
        save_path: Path | None = None,
        **kwargs,
    ) -> GradescopeJson:
        """Convert a list of test results to Gradescope JSON.

        :param results: The test results.
        :param score: The score obtained from the submission.
        :param save_path: The path to save the Gradescope JSON to.
        :param kwargs: The keyword arguments to pass to the constructor.
        :return: The Gradescope JSON.
        """
        gs_json = cls(
            score=score,
            tests=[GradescopeTestJson.from_test_result(result) for result in results],
            **kwargs,
        )

        if save_path is not None:
            with open(save_path, "w") as f:
                f.write(gs_json.to_json())  # type: ignore

        return gs_json

    @classmethod
    def from_error(
        cls, error: InternalError | StudentError, save_path: Path | None = None
    ) -> GradescopeJson:
        """Convert an error to Gradescope JSON.

        :param error: The error to convert.
        :param save_path: The path to save the Gradescope JSON to.
        :return: The Gradescope JSON.
        """
        gs_json = cls(
            score=0,
            tests=[],
            output=error.format(),
        )

        if save_path is not None:
            with open(save_path, "w") as f:
                f.write(gs_json.to_json())  # type: ignore

        return gs_json
