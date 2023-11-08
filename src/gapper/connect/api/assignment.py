from dataclasses import dataclass
from typing import Any

from requests import Session

from gapper.connect.api.mixins import SessionHolder


@dataclass
class GSAssignment(SessionHolder):
    name: str
    aid: str
    points: str
    submissions: str
    percent_graded: str
    complete: bool
    regrades_on: bool

    def __init__(
        self,
        name: str,
        aid: str,
        points: str,
        submissions: str,
        percent_graded: str,
        complete: bool,
        regrades_on: bool,
        session: Session | None = None,
    ):
        super().__init__(session)
        self.name = name
        self.aid = aid
        self.points = points
        self.submissions = submissions
        self.percent_graded = percent_graded
        self.complete = complete
        self.regrades_on = regrades_on

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, GSAssignment):
            return self.aid == other.aid
        return False

    def __hash__(self) -> int:
        return hash(self.aid)
