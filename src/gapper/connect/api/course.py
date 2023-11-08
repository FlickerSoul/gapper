import datetime
from dataclasses import dataclass
from typing import Any, Dict, Literal

from bs4 import BeautifulSoup
from requests import Session
from requests_toolbelt import MultipartEncoder

from gapper.connect.api.assignment import GSAssignment
from gapper.connect.api.mixins import SessionHolder
from gapper.connect.api.utils import DATE_TIME_FORMAT


@dataclass
class GSCourse(SessionHolder):
    cid: str
    name: str
    shortname: str
    year: str
    assignment_count: str
    inactive: bool

    def __init__(
        self,
        cid: str,
        name: str,
        shortname: str,
        year: str,
        assignment_count: str,
        inactive: bool,
        session: Session | None = None,
    ) -> None:
        super().__init__(session)
        self.cid = cid
        self.name = name
        self.shortname = shortname
        self.year = year
        self.assignment_count = assignment_count
        self.inactive = inactive
        self.assignments: Dict[str, GSAssignment] = {}

    def get_assignments(self) -> None:
        self.assignments.clear()

        assignment_resp = self._session.get(
            "https://www.gradescope.com/courses/" + self.cid + "/assignments"
        )
        parsed_assignment_resp = BeautifulSoup(assignment_resp.text, "html.parser")

        assignment_table = []
        for assignment_row in parsed_assignment_resp.findAll(
            "tr", class_="js-assignmentTableAssignmentRow"
        ):
            row = []
            for td in assignment_row.findAll("td"):
                row.append(td)
            assignment_table.append(row)

        for row in assignment_table:
            name = row[0].text
            aid = row[0].find("a").get("href").rsplit("/", 1)[1]
            points = row[1].text
            # TODO: (released,due) = parse(row[2])
            submissions = row[3].text
            percent_graded = row[4].text
            complete = (
                True if "workflowCheck-complete" in row[5].get("class") else False
            )
            regrades_on = False if row[6].text == "OFF" else True
            self.collect_assignment(
                name, aid, points, submissions, percent_graded, complete, regrades_on
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
            "assignment[release_date_string]": release_date.strftime(DATE_TIME_FORMAT),
            "assignment[due_date_string]": due_date.strftime(DATE_TIME_FORMAT),
            "assignment[allow_late_submissions]": "0",
            "assignment[group_submission]": "0",
            "assignment[leaderboard_enabled]": "0",
        }

        if late_submission_date is not None:
            assignment_dict["assignment[allow_late_submissions]"] = "1"
            assignment_dict["assignment[hard_due_date_string]"] = (
                late_submission_date.strftime(DATE_TIME_FORMAT),
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
        complete: bool,
        regrades_on: bool,
    ):
        self.assignments[name] = GSAssignment(
            name,
            aid,
            points,
            submissions,
            percent_graded,
            complete,
            regrades_on,
            self._session,
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, GSCourse):
            return self.cid == other.cid
        return False

    def __hash__(self) -> int:
        return hash(self.cid)
