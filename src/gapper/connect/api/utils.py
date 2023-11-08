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


DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M"
