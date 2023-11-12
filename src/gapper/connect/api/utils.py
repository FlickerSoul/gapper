import enum
from typing import NamedTuple

import requests
from bs4 import BeautifulSoup


def get_authenticity_token(session: requests.Session) -> str:
    init_resp = session.get("https://www.gradescope.com/", verify=False)
    parsed_init_resp = BeautifulSoup(init_resp.text, "html.parser")
    for form in parsed_init_resp.find_all("form"):
        if form.get("action") == "/login":
            for inp in form.find_all("input"):
                if inp.get("name") == "authenticity_token":
                    auth_token = inp.get("value")
                    return auth_token

    raise ValueError("Could not find authenticity token")


SUBMIT_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M"
PARSE_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%:z"


class ImageChoice(NamedTuple):
    image: str
    id: int


class OSChoices(enum.Enum):
    UbuntuV1804 = ImageChoice("gradescope/autograder-base:ubuntu-18.04", 1)
    UbuntuV2004 = ImageChoice("gradescope/autograder-base:ubuntu-20.04", 2)
    UbuntuV2204 = ImageChoice("gradescope/autograder-base:ubuntu-22.04", 3)

    @property
    def name(self) -> str:
        match self:
            case OSChoices.UbuntuV1804:
                return "Ubuntu 18.04"
            case OSChoices.UbuntuV2004:
                return "Ubuntu 20.04"
            case OSChoices.UbuntuV2204:
                return "Ubuntu 22.04"
