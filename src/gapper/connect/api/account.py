from __future__ import annotations

import logging
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Self

import requests
import yaml
from bs4 import BeautifulSoup, Tag
from dataclasses_json import config, dataclass_json

from gapper.connect.api.course import GSCourse
from gapper.connect.api.mixins import SessionHolder
from gapper.connect.api.utils import get_authenticity_token


@dataclass_json
@dataclass
class GSAccount(SessionHolder):
    email: str
    cookies: Optional[Dict[str, str]]
    courses: Dict[str, GSCourse]
    password: str = field(
        default="", metadata=config(exclude=lambda x: True), init=False
    )

    def __init__(
        self,
        email: str,
        password: str = "",
        cookies: Dict[str, str] | None = None,
        courses: Dict[str, GSCourse] | None = None,
        *,
        session: requests.Session | None = None,
    ) -> None:
        super().__init__(session)
        self.email = email
        self.password = password
        self.cookies = cookies
        self.courses: Dict[str, GSCourse] = courses or {}
        self._logger = logging.getLogger(
            f"gapper.connect.api.account.GSAccount_{self.email}"
        )

    async def login(self, remember_me: bool = True) -> Self:
        """Login to Gradescope.

        :param remember_me: Whether to remember the login session.
        :raises ValueError: If login fails.
        """
        if self.cookies is not None and self.cookies:
            self.load_cookie(self.cookies)
            if self.confirm_login():
                self._logger.debug("Existing cookie is valid")
                return self
            else:
                self._logger.debug("Login failed: cookie invalid")
                self.clear_cookie()
                self._logger.debug("Cleared cookie")
        else:
            self._logger.debug("No cookie found, logging in with email and password")

        login_resp = self._session.post(
            "https://www.gradescope.com/login",
            data=self.serialize_login_params(
                self._session, self.email, self.password, remember_me
            ),
            allow_redirects=False,
        )

        if (
            login_resp.status_code == requests.codes.found
            and len(self._session.cookies) > 1
        ):
            self._logger.debug("Login seems successfully executed")
            self._logger.debug(
                'Trying confirm login by accessing "https://www.gradescope.com/"'
            )
            if self.confirm_login():
                self.cookies = self.get_cookie()
                self._logger.debug("Saved cookie to account")
                return self
        else:
            self._logger.debug(
                "Login failed: login response history is empty, status code %d",
                login_resp.status_code,
            )

        raise ValueError("Login failed")

    def confirm_login(self) -> bool:
        confirm_resp = self._session.get(
            "https://www.gradescope.com/account", allow_redirects=False
        )
        if confirm_resp.status_code == requests.codes.ok:
            self._logger.debug("Login confirmed")
            return True
        else:
            self._logger.debug(
                'Login failed: "https://www.gradescope.com/" returned status code %d',
                confirm_resp.status_code,
            )

        return False

    async def get_admin_courses(self) -> None:
        """Get the list of courses the account is administrating."""
        # Get account page and parse it using bs4
        account_resp = self._session.get("https://www.gradescope.com/account")
        parsed_account_resp = BeautifulSoup(account_resp.text, "html.parser")

        # Get instructor course data
        instructor_courses = parsed_account_resp.find(
            "h1", class_="pageHeading", string="Instructor Courses"
        ).findNext("div", attrs={"class": "courseList"})

        for course_header in instructor_courses.find_all(  # type: Tag
            "div", class_="courseList--term"
        ):
            term, year = course_header.text.split(" ", 1)

            course_container: Tag = course_header.findNext(
                "div", class_="courseList--coursesForTerm"
            )

            inactive = (
                course_header.parent.get("class") == "courseList--inactiveCourses"
            )

            for course in course_container.findChildren("a", class_="courseBox"):
                shortname = course.find("h3", class_="courseBox--shortname").text
                name = course.find("div", class_="courseBox--name").text
                cid = course.get("href").split("/")[-1]
                assignment_count = course.find(
                    "div", class_="courseBox--assignments"
                ).text
                self._logger.debug(
                    f"found course '{name}' with {cid} and shortname {shortname}, in year {year}"
                )

                self.collect_course(
                    cid, name, shortname, term, year, assignment_count, inactive
                )

    def collect_course(
        self,
        cid: str,
        name: str,
        shortname: str,
        term: str,
        year: str,
        assignment_count: str,
        inactive: bool,
    ) -> None:
        self.courses[cid] = GSCourse(
            cid,
            name,
            shortname,
            term,
            year,
            assignment_count,
            inactive,
            session=self._session,
        )

    @staticmethod
    def serialize_login_params(session, email, password, remember_me: bool) -> str:
        """

        :param session:
        :param email:
        :param password:
        :param remember_me:
        :return:
        """
        try:
            auth_token = get_authenticity_token(session)
        except ValueError as e:
            raise ValueError(
                "Cannot serialize login params because authenticity token is not found. "
                "It's possible you have logged in."
            ) from e

        login_data = {
            "utf8": "✓",
            "authenticity_token": auth_token,
            "session[email]": email,
            "session[password]": password,
            "session[remember_me]": "0",
            "commit": "Log In",
            "session[remember_me_sso]": "0",
        }

        login_params = [item for item in login_data.items()]

        if remember_me:
            login_params.append(("session[remember_me]", "1"))

        return str(urllib.parse.urlencode(login_params))

    def load_session(self, session: requests.Session) -> Self:
        super().load_session(session)
        for course in self.courses.values():
            course.load_session(session)

        return self

    def spawn_session(self) -> Self:
        super().spawn_session()
        self.load_session(self._session)

        return self

    @classmethod
    def from_yaml(cls, path: Path) -> GSAccount:
        """Load the account manager from a yaml file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data, infer_missing=True)

    def to_yaml(self, path: Path | None = None) -> str:
        yaml_data = yaml.dump(self.to_dict())
        path.parent.mkdir(exist_ok=True, parents=True)

        with open(path, "w") as f:
            f.write(yaml_data)

        return yaml_data
