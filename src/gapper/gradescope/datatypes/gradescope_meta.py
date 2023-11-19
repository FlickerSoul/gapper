"""The JSON schemas for Gradescope's metadata."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Literal, Optional

from dataclasses_json import config, dataclass_json
from marshmallow import fields

from gapper.gradescope.datatypes.gradescope_output import GradescopeJson

_gradescope_meta_logger = logging.getLogger("gapper.gradescope_meta")


@dataclass_json
@dataclass(frozen=True)
class GradescopeAssignmentMetadata:
    """The JSON schema for Gradescope's assignment settings.

    :param due_date: The assignment's due date.
    :param group_size: The maximum group size on a group assignment.
    :param group_submission: Whether group submission is allowed.
    :param id: The assignment's ID.
    :param course_id: The course's ID.
    :param late_due_date: The late due date, or None if late submission disallowed.
    :param release_date: The assignment's release date.
    :param title: The assignment's title.
    :param total_points: The total point value of the assignment.
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

    :param email: The submitter's email.
    :param id: The submitter's ID.
    :param name: The submitter's name.
    """

    email: str
    id: int
    name: str


@dataclass_json
@dataclass(frozen=True)
class GradescopePreviousSubmission:
    """The JSON schema for a previous submission record.

    :param submission_time: The time of the previous submission.
    :param score: The previous submission's score.
    :param results: The results.json file from the previous submission.
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
    :param id: The submission's ID.
    :param created_at: The time the submission was created.
    :param assignment: The assignment's metadata.
    :param submission_method: The submission method.
    :param users: The submitters' metadata.
    :param previous_submissions: The previous submissions' metadata.
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
        """Load the submission metadata from a file.

        :param path: The path to load the submission metadata from.
        """
        obj = cls.from_json(path.read_text())  # type: ignore
        _gradescope_meta_logger.debug(
            f"Submission metadata loaded from {path.absolute()}"
        )
        return obj
