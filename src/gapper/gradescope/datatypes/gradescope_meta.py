from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime
from pathlib import Path
from typing import Optional, Literal, List

from dataclasses_json import dataclass_json, config
from marshmallow import fields

from gapper.gradescope.datatypes.gradescope_output import GradescopeJson


@dataclass_json
@dataclass(frozen=True)
class GradescopeAssignmentMetadata:
    """The JSON schema for Gradescope's assignment settings.

    Attributes
    ----------
    due_date : datetime
        The assignment's due date.
    group_size : Optional[int]
        The maximum group size on a group assignment.
    group_submission : bool
        Whether group submission is allowed.
    id : int
        The assignment's ID.
    course_id : int
        The course's ID.
    late_due_date : Optional[datetime]
        The late due date, or None if late submission disallowed.
    release_date : datetime
        The assignment's release date.
    title : str
        The assignment's title.
    total_points : float
        The total point value of the assignment.
    """

    due_date: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,  # type: ignore
            mm_field=fields.DateTime(format="iso"),
        )
    )
    group_size: Optional[int]
    group_submission: bool
    id: int
    course_id: int
    late_due_date: Optional[datetime] = field(
        metadata=config(
            encoder=lambda s: datetime.isoformat(s) if s else None,
            decoder=lambda s: datetime.fromisoformat(s) if s else None,  # type: ignore
            mm_field=fields.DateTime(format="iso"),
        )
    )
    release_date: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,  # type: ignore
            mm_field=fields.DateTime(format="iso"),
        )
    )
    title: str
    total_points: float = field(metadata=config(encoder=str, decoder=float))


@dataclass_json
@dataclass(frozen=True)
class GradescopeAssignmentUser:
    """The JSON schema for a 'user' (submitter) of a Gradescope assignment.

    Attributes
    ----------
    email : str
        The submitter's email.
    id : int
        The submitter's ID.
    name : str
        The submitter's name.
    """

    email: str
    id: int
    name: str


@dataclass_json
@dataclass(frozen=True)
class GradescopePreviousSubmission:
    """The JSON schema for a previous submission record.

    Attributes
    ----------
    submission_time : datetime
        The time of the previous submission.
    score : float
        The previous submission's score.
    results : GradescopeJson
        The results.json file from the previous submission.
    """

    submission_time: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,  # type: ignore
            mm_field=fields.DateTime(format="iso"),
        )
    )
    score: float
    results: GradescopeJson


@dataclass_json
@dataclass(frozen=True)
class GradescopeSubmissionMetadata:
    """The JSON schema for Gradescope's submission metadata.

    See Also https://gradescope-autograders.readthedocs.io/en/latest/submission_metadata/
    """

    id: int
    created_at: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,  # type: ignore
            mm_field=fields.DateTime(format="iso"),
        )
    )
    assignment: GradescopeAssignmentMetadata
    submission_method: Literal["upload", "GitHub", "Bitbucket"]
    users: List[GradescopeAssignmentUser]
    previous_submissions: List[GradescopePreviousSubmission]

    @classmethod
    def from_file(cls, path: Path) -> GradescopeSubmissionMetadata:
        """Load the submission metadata from a file."""
        return cls.from_json(path.read_text())  # type: ignore
