from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Literal, List, TYPE_CHECKING

from dataclasses_json import dataclass_json

from gapper.core.errors import InternalError


if TYPE_CHECKING:
    from gapper.core.test_result import TestResult
    from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata


VisibilityType = Literal["hidden", "after_due_date", "after_published", "visible"]
FormatType = Literal["text", "html", "simple_format", "md", "ansi"]
PassStateType = Literal["passed", "failed"]


@dataclass_json
@dataclass
class GradescopeTestJson:
    """The JSON schema for a single Test.

    Attributes
    ----------
    score : Optional[float]
        The test's score. Required if no top-level score is set.
    max_score : Optional[float]
        The max score for the test.
    name : Optional[str]
        The test's name.
    output : Optional[str]
        Human-readable text output of the test.
    tags : Optional[List[str]]
        Tags for the test.
    visibility : str
        The test's visibility. "hidden", "visible", "after_due_date", "after_published"
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

    Attributes
    ----------
    tests : List[_GradescopeJsonTest]
        The tests for the problem. Required if no global score provided.
    score : Optional[float]
        The overall score. Required if any test has no set score.
    execution_time : Optional[int]
        The execution time of all the tests, in seconds.
    output : Optional[str]
        The top-level, human-readable text output for all the problems.
    visibility : Optional[str]
        The default visibility for each test. Overridden by test-specific settings.
    stdout_visibility : Optional[str]
        Whether to show stdout for the tests. Same options as for visibility.
    """

    score: Optional[float] = None
    tests: list[GradescopeTestJson] = field(default_factory=list)
    execution_time: Optional[int] = None
    output: Optional[str] = None
    visibility: VisibilityType = "visible"
    stdout_visibility: Optional[str] = None

    @staticmethod
    def synthesize_score(results: List[TestResult], total_score: float) -> float:
        results_with_score = []
        results_with_weight = []

        max_score_sum = 0.0
        weight_sum = 0

        for res in results:
            if res.max_score is None and res.weight is None:
                raise InternalError(
                    "The max_score and weight of a test (result) cannot both be None."
                )

            if res.max_score is not None and res.weight is not None:
                raise InternalError(
                    "The max_score and weight of a test (result) cannot both be set."
                )

            if res.max_score is not None:
                results_with_score.append(res)
                max_score_sum += res.max_score
            elif res.weight is not None:
                results_with_weight.append(res)
                weight_sum += res.weight
            else:
                raise InternalError(
                    f"The max_score and weight of a test (result) cannot both be None, "
                    f"but {res.rich_test_name} has both being None."
                )

        if max_score_sum > total_score:
            raise InternalError(
                f"The sum of the scores ({max_score_sum}) of all tests must be less than or equal to the "
                f"total points for the assignment ({total_score})."
            )

        remaining_score = total_score - max_score_sum

        for res in results_with_weight:
            assert res.weight is not None
            res.max_score = res.weight * remaining_score / weight_sum
            res.weight = None

        for res in results:
            if res.score is not None:
                if res.score < 0:
                    raise InternalError(
                        f"Test {res.name} has a negative score ({res.score})."
                    )

                if res.extra_score is not None:
                    raise InternalError(
                        f"In test ({res.name}) extra score is ignored because a score is set through custom test check."
                    )

                continue

            assert res.max_score is not None

            # interpret score with pass status
            if res.pass_status == "passed":
                res.score = (
                    res.max_score + 0 if res.extra_score is None else res.extra_score
                )
            else:
                res.score = 0

        return sum((res.score for res in results), 0.0)

    @classmethod
    def from_test_results(
        cls,
        results: List[TestResult],
        metadata: GradescopeSubmissionMetadata,
        save_path: Path | None = None,
        **kwargs,
    ) -> GradescopeJson:
        # this has to be calculated first
        # so that we can use it to calculate the score
        score = cls.synthesize_score(results, metadata.assignment.total_points)
        gs_json = cls(
            score=score,
            tests=[GradescopeTestJson.from_test_result(result) for result in results],
            **kwargs,
        )

        if save_path is not None:
            with open(save_path, "w") as f:
                f.write(gs_json.to_json())  # type: ignore

        return gs_json
