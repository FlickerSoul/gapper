from __future__ import annotations

import datetime
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Self, TypedDict

import requests
from bs4 import BeautifulSoup
from dataclasses_json import dataclass_json
from requests import Session
from requests_toolbelt import MultipartEncoder

from gapper.connect.api.assignment import GSAssignment
from gapper.connect.api.mixins import SessionHolder
from gapper.connect.api.utils import SUBMIT_DATE_TIME_FORMAT


class SubmissionWindow(TypedDict):
    release_date: str
    due_date: str
    hard_due_date: str | None
    time_limit: str | None


class CourseInfo(TypedDict):
    id: str
    url: str
    title: str
    total_points: str
    is_published: bool
    num_active_submissions: int
    grading_progress: float
    submission_window: SubmissionWindow


@dataclass_json
@dataclass
class GSCourse(SessionHolder):
    cid: str
    name: str
    shortname: str
    term: str
    year: str
    assignment_count: str
    inactive: bool
    assignments: Dict[str, GSAssignment]

    def __init__(
        self,
        cid: str,
        name: str,
        shortname: str,
        term: str,
        year: str,
        assignment_count: str,
        inactive: bool,
        assignments: Dict[str, GSAssignment] | None = None,
        *,
        session: Session | None = None,
    ) -> None:
        super().__init__(session)
        self.cid = cid
        self.name = name
        self.shortname = shortname
        self.term = term
        self.year = year
        self.assignment_count = assignment_count
        self.inactive = inactive
        self.assignments: Dict[str, GSAssignment] = assignments or {}

    async def get_assignments(self) -> None:
        self.assignments.clear()

        assignment_resp = self._session.get(
            f"https://www.gradescope.com/courses/{self.cid}/assignments"
        )
        parsed_assignment_resp = BeautifulSoup(assignment_resp.text, "html.parser")

        table_data_div = parsed_assignment_resp.find(
            attrs={"data-react-class": "AssignmentsTable"}
        )

        table_prop_data: List[CourseInfo] = json.loads(
            table_data_div.get("data-react-props")
        )["table_data"]

        for row in table_prop_data:
            name = row["title"]
            aid = row["url"].rsplit("/", 1)[-1]
            points = row["total_points"]
            release_date = row["submission_window"]["release_date"]
            due_date = row["submission_window"]["due_date"]
            hard_due_date = row["submission_window"]["hard_due_date"]
            submissions = str(row["num_active_submissions"])
            percent_graded = str(row["grading_progress"])
            published = row["is_published"]

            self.collect_assignment(
                name,
                aid,
                points,
                submissions,
                percent_graded,
                published,
                release_date,
                due_date,
                hard_due_date,
            )

    def add_assignment(
        self,
        name: str,
        points: int,
        release_date: datetime.datetime,
        due_date: datetime.datetime,
        late_submission_date: datetime.datetime | None = None,
        group_size: int | None = None,
        leaderboard_entries: int | None = None,
        when_to_create_rubric: Literal["before_submissions", "while_grading"]
        | None = None,
    ):
        assignment_resp = self._session.get(
            "https://www.gradescope.com/courses/" + self.cid + "/assignments"
        )
        parsed_assignment_resp = BeautifulSoup(assignment_resp.text, "html.parser")
        authenticity_token = parsed_assignment_resp.find(
            "meta", attrs={"name": "csrf-token"}
        ).get("content")

        assignment_dict = {
            "authenticity_token": authenticity_token,
            "assignment[type]": "ProgrammingAssignment",
            "assignment[title]": name,
            "assignment[submissions_anonymized]": "0",
            "assignment[total_points]": points,
            "assignment[manual_grading": "0",
            "assignment[student_submission]": "1",
            "assignment[release_date_string]": release_date.strftime(
                SUBMIT_DATE_TIME_FORMAT
            ),
            "assignment[due_date_string]": due_date.strftime(SUBMIT_DATE_TIME_FORMAT),
            "assignment[allow_late_submissions]": "0",
            "assignment[group_submission]": "0",
            "assignment[leaderboard_enabled]": "0",
        }

        if late_submission_date is not None:
            assignment_dict["assignment[allow_late_submissions]"] = "1"
            assignment_dict["assignment[hard_due_date_string]"] = (
                late_submission_date.strftime(SUBMIT_DATE_TIME_FORMAT),
            )

        if group_size is not None:
            assignment_dict["assignment[group_submission]"] = "1"
            assignment_dict["assignment[group_size]"] = str(group_size)

        if leaderboard_entries:
            assignment_dict["assignment[leaderboard_enabled]"] = "1"
            assignment_dict["assignment[leaderboard_max_entries]"] = str(
                leaderboard_entries
            )
        if when_to_create_rubric is not None:
            assignment_dict["assignment[when_to_create_rubric]"] = when_to_create_rubric

        multipart = MultipartEncoder(fields=assignment_dict)

        assignment_resp = self._session.post(
            "https://www.gradescope.com/courses/" + self.cid + "/assignments",
            data=multipart,
            headers={"Content-Type": multipart.content_type},
        )

        self.get_assignments()

    def collect_assignment(
        self,
        name: str,
        aid: str,
        points: str,
        submissions: str,
        percent_graded: str,
        published: bool,
        release_date: str,
        due_date: str,
        hard_due_date: str | None = None,
    ):
        self.assignments[aid] = GSAssignment(
            self.cid,
            name,
            aid,
            points,
            submissions,
            percent_graded,
            published,
            release_date,
            due_date,
            hard_due_date,
            session=self._session,
        )

    def load_session(self, session: requests.Session) -> Self:
        super().load_session(session)
        for assignment in self.assignments.values():
            assignment.load_session(session)

        return self

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, GSCourse):
            return self.cid == other.cid
        return False

    def __hash__(self) -> int:
        return hash(self.cid)
