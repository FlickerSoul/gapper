from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Literal, List

from dataclasses_json import dataclass_json

VisibilityType = Literal["hidden", "after_due_date", "after_published", "visible"]


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

    score: Optional[float] = None
    max_score: Optional[float] = None
    status: Optional[Literal["passed", "failed"]] = None
    name: Optional[str] = None
    number: Optional[float] = None
    output: Optional[str] = None
    tags: Optional[str] = None
    visibility: VisibilityType = "visible"


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

    tests: List[GradescopeTestJson] = field(default_factory=list)
    score: Optional[float] = None
    execution_time: Optional[int] = None
    output: Optional[str] = None
    visibility: VisibilityType = "visible"
    stdout_visibility: Optional[str] = None
