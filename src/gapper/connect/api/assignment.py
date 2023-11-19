"""This module contains the classes for Gradescope assignments."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, TypedDict

import requests
from bs4 import BeautifulSoup
from dataclasses_json import dataclass_json
from requests_toolbelt import MultipartEncoder

from gapper.connect.api.mixins import SessionHolder
from gapper.connect.api.utils import OSChoices

_assignment_logger = logging.getLogger("gapper.connect.api.assignment")

NO_IMAGE_REGEX = re.compile(r"gon\.image *= *null *;?")
IMAGE_REGEX = re.compile(
    r"gon\.image *= *{.*\"name\" *: *\"gradescope/autograders:.*-(?P<docker_id>\d+)\""
)


class DockerStatusJson(TypedDict):
    """The json response of the docker status of upload."""

    id: int
    assignment_id: int
    name: str
    status: str
    stdout: str
    stderr: str
    created_at: str
    updated_at: str


@dataclass_json
@dataclass
class GSAssignmentEssential(SessionHolder):
    """The essential information of a Gradescope assignment."""

    cid: str
    aid: str
    docker_id: str | None

    def __init__(
        self,
        cid: str,
        aid: str,
        docker_id: str | None = None,
        *,
        session: requests.Session | None = None,
    ) -> None:
        """Create a Gradescope assignment essential object.

        :param cid: The course id of the Gradescope assignment.
        :param aid: The assignment id of the Gradescope assignment.
        :param docker_id: The docker id of the assignment.
        :param session: The session to use.
        """
        super().__init__(session)
        self.cid = cid
        self.aid = aid
        self.docker_id = docker_id
        self._logger = _assignment_logger.getChild(f"GSAssignmentEssential_{self.aid}")

    async def upload_autograder(self, path: Path, os_choice: OSChoices) -> None:
        """Upload the autograder to the assignment.

        :param path: The path to the autograder zip file.
        :param os_choice: The choice of the operating system.
        """
        if not path.exists():
            raise FileNotFoundError(f"File {path} does not exist when uploading")
        if not path.is_file() or not path.suffix == ".zip":
            raise ValueError(f"File {path} is not a zip file")

        autograder_config = self._session.get(
            "https://www.gradescope.com/courses/"
            + self.cid
            + "/assignments/"
            + self.aid
            + "/configure_autograder"
        )
        autograder_config_resp = BeautifulSoup(autograder_config.text, "html.parser")
        autograder_form = autograder_config_resp.find(
            "form", attrs={"class": "js-autograderForm"}
        )
        authenticity_token = autograder_form.find(
            "input", attrs={"name": "authenticity_token"}
        ).get("value")

        autograder_dict: Dict[str, str] = {
            "utf8": "â",
            "_method": "patch",
            "authenticity_token": authenticity_token,
            "configuration": "zip",
            "autograder_zip": (path.name, path.read_bytes(), "text/plain"),
            "base_image_id": str(os_choice.value.id),
            "assignment[image_name]": os_choice.value.image,
        }

        multipart = MultipartEncoder(fields=autograder_dict)

        response = self._session.post(
            f"https://www.gradescope.com/courses/{self.cid}/assignments/{self.aid}/",
            data=multipart,
            headers={"Content-Type": multipart.content_type},
        )

        if response.status_code != requests.codes.ok:
            raise ValueError(f"Upload failed with status code {response.status_code}")

    def get_active_docker_id(self) -> str | None:
        """Get the active docker id of the assignment."""
        if self.docker_id is None:
            autograder_config = self._session.get(
                "https://www.gradescope.com/courses/"
                + self.cid
                + "/assignments/"
                + self.aid
                + "/configure_autograder"
            )

            if autograder_config.status_code != requests.codes.ok:
                self._logger.debug(
                    f"Failed to get autograder config. The status code is {autograder_config.status_code}"
                )
                return None

            self._logger.debug("Got autograder config")
            self._logger.debug(autograder_config.text)

            if NO_IMAGE_REGEX.search(autograder_config.text) is not None:
                self._logger.debug("No image found")
                return None

            id_match = IMAGE_REGEX.search(autograder_config.text)
            if id_match is None:
                self._logger.debug("No image found")
                self._logger.error(
                    "Cannot find docker image id. Please notify the developer of this error."
                )
                return None

            self.docker_id = id_match.groupdict()["docker_id"]

        return self.docker_id

    def get_docker_build_status(self) -> DockerStatusJson | None:
        """Get the docker build status of the assignment."""
        docker_id = self.get_active_docker_id()
        if docker_id is None:
            return None

        return self._session.get(
            f"https://www.gradescope.com/courses/{self.cid}/assignments/{self.aid}/docker_images/{docker_id}.json"
        ).json()

    def __eq__(self, other: Any) -> bool:
        """Check if two GSAssignments are equal."""
        if isinstance(other, GSAssignmentEssential):
            return self.cid == other.cid and self.aid == other.aid
        return False

    def __hash__(self) -> int:
        return hash(f"{self.cid}{self.aid}")


@dataclass_json
@dataclass
class GSAssignment(GSAssignmentEssential):
    """The Gradescope assignment with detailed information."""

    name: str
    points: str
    submissions: str
    percent_graded: str
    published: bool
    release_date: str
    due_date: str
    hard_due_date: str | None

    def __init__(
        self,
        cid: str,
        name: str,
        aid: str,
        points: str,
        submissions: str,
        percent_graded: str,
        published: bool,
        release_date: str,
        due_date: str,
        hard_due_date: str | None,
        docker_id: str | None = None,
        *,
        session: requests.Session | None = None,
    ) -> None:
        """Create a Gradescope assignment object.

        :param cid: The course id of the Gradescope assignment.
        :param name: The name of the Gradescope assignment.
        :param aid: The assignment id of the Gradescope assignment.
        :param points: The points of the Gradescope assignment.
        :param submissions: The submissions of the Gradescope assignment.
        :param percent_graded: The percent graded of the Gradescope assignment.
        :param published: Whether the Gradescope assignment is published.
        :param release_date: The release date of the Gradescope assignment.
        :param due_date: The due date of the Gradescope assignment.
        :param hard_due_date: The late due date of the Gradescope assignment.
        :param docker_id: The docker id of the Gradescope assignment.
        :param session: The session to use.
        """
        super().__init__(cid, aid, docker_id, session=session)
        self.name = name
        self.points = points
        self.submissions = submissions
        self.percent_graded = percent_graded
        self.published = published
        self.release_date = release_date
        self.due_date = due_date
        self.hard_due_date = hard_due_date
        self._logger = _assignment_logger.getChild(f"GSAssignment_{self.aid}")
