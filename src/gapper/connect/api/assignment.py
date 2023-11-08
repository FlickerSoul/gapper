from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, TypedDict

import requests
from bs4 import BeautifulSoup
from requests_toolbelt import MultipartEncoder

from gapper.connect.api.utils import OSChoices

if TYPE_CHECKING:
    from gapper.connect.api.course import GSCourse


class DockerStatusJson(TypedDict):
    id: int
    assignment_id: int
    name: str
    status: str
    stdout: str
    stderr: str
    created_at: str
    updated_at: str


@dataclass
class GSAssignment:
    name: str
    aid: str
    points: str
    submissions: str
    percent_graded: str
    published: bool
    release_date: str
    due_date: str
    hard_due_date: str | None

    def __init__(
        self,
        name: str,
        aid: str,
        points: str,
        submissions: str,
        percent_graded: str,
        published: bool,
        release_date: str,
        due_date: str,
        hard_due_date: str | None,
        course: GSCourse,
    ):
        self.name = name
        self.aid = aid
        self.points = points
        self.submissions = submissions
        self.percent_graded = percent_graded
        self.published = published
        self.release_date = release_date
        self.due_date = due_date
        self.hard_due_date = hard_due_date
        self.course = course

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, GSAssignment):
            return self.aid == other.aid
        return False

    def __hash__(self) -> int:
        return hash(self.aid)

    def upload_autograder(self, path: Path, os_choice: OSChoices) -> None:
        if not path.exists():
            raise FileNotFoundError(f"File {path} does not exist when uploading")
        if not path.is_file() or not path.suffix == ".zip":
            raise ValueError(f"File {path} is not a zip file")

        autograder_config = self.course._session.get(
            "https://www.gradescope.com/courses/"
            + self.course.cid
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

        response = self.course._session.post(
            f"https://www.gradescope.com/courses/{self.course.cid}/assignments/{self.aid}/",
            data=multipart,
            headers={"Content-Type": multipart.content_type},
        )

        if response.status_code != requests.codes.ok:
            raise ValueError(f"Upload failed with status code {response.status_code}")

    def get_active_docker_id(self) -> str | None:
        autograder_config = self.course._session.get(
            "https://www.gradescope.com/courses/"
            + self.course.cid
            + "/assignments/"
            + self.aid
            + "/configure_autograder"
        )

        autograder_config_resp = BeautifulSoup(autograder_config.text, "html.parser")

        docker_image_tag = autograder_config_resp.find(
            "input", id_="assignment_image_name"
        )
        image_name = docker_image_tag.get("value", None)
        if image_name is None:
            return None

        return image_name.rsplit("-")[-1]

    def get_docker_build_status(self) -> DockerStatusJson | None:
        docker_id = self.get_active_docker_id()
        if docker_id is None:
            return None

        return self.course._session.get(
            f"https://www.gradescope.com/courses/{self.course.cid}/assignments/{self.aid}/docker_images/{docker_id}.json"
        ).json()
