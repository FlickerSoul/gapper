from dataclasses import dataclass, field
from typing import Dict, Optional, Self

import requests
from dataclasses_json import config, dataclass_json
from requests.utils import cookiejar_from_dict, dict_from_cookiejar


@dataclass_json
@dataclass
class SessionHolder:
    _session: Optional[requests.Session] = field(
        metadata=config(exclude=lambda x: True), init=False, default=None
    )

    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session

    @property
    def session(self) -> requests.Session | None:
        return self._session

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
