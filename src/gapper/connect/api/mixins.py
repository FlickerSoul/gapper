from typing import Dict, Self

import requests
from requests.utils import cookiejar_from_dict, dict_from_cookiejar


class SessionHolder:
    def __init__(self, session: requests.Session = None) -> None:
        self._session = session

        if self._session is None:
            self.spawn_session()

        self.require_verify()

    def load_session(self, session: requests.Session) -> Self:
        self._session = session
        return self

    def spawn_session(self) -> Self:
        self._session = requests.Session()
        return self

    def no_verify(self) -> Self:
        self._session.verify = False
        return self

    def require_verify(self) -> Self:
        self._session.verify = True
        return self

    def get_cookie(self) -> Dict[str, str]:
        return dict_from_cookiejar(self._session.cookies)

    def load_cookie(self, d: Dict[str, str]) -> None:
        self._session.cookies.update(cookiejar_from_dict(d))

    def clear_cookie(self) -> None:
        self._session.cookies.clear()
