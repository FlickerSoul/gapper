"""The Gradescope connect decorator and helpers."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, overload

from gapper.connect.api.utils import extract_cid_aid_from_url

if TYPE_CHECKING:
    from gapper.core.problem import Problem

_gs_connect_logger = logging.getLogger("gapper.core.problem.extras.gradescope_connect")


@dataclass(frozen=True)
class GSConnectConfig:
    """The configuration for Gradescope connect."""

    cid: str
    aid: str


def build_connect_config(url_or_cid: str, aid: str | None = None) -> GSConnectConfig:
    """Build the connect arguments.

    :param url_or_cid: The url when aid is not specified, or the course id of the Gradescope assignment.
        The format of the url should be
        https://www.gradescope.com/courses/<cid>/assignments/<aid>[anything]

                connect('12443', '112358')  # specify cid and aid
                connect('https://www.gradescope.com/courses/12443/assignments/112358')  # specify url

    :param aid: The assignment id of the Gradescope assignment. It should be specified when url_or_cid is a cid.
    """
    if aid is None:
        url = url_or_cid
        cid, aid = extract_cid_aid_from_url(url)
        _gs_connect_logger.debug(f"Extracted cid {cid} and aid {aid} from url {url}")
    else:
        cid = url_or_cid
        _gs_connect_logger.debug(f"Using cid {cid} and aid {aid} from user input.")

    if not cid or not aid:
        raise ValueError(
            "Must specify both cid and aid at the same time. Or specify a url."
        )
    if (
        not cid.isdigit() or not aid.isdigit()
    ):  # not perfect for 0-9 checking but it's fine
        raise ValueError("cid and aid must be digits.")

    return GSConnectConfig(cid=cid, aid=aid)


@overload
def gs_connect[T: Problem](cid: str, aid: str) -> Callable[[T], T]:
    """Connect a problem to a Gradescope assignment.

    :param cid: The course id of the Gradescope assignment.
    :param aid: The assignment id of the Gradescope assignment.
    """


@overload
def gs_connect[T: Problem](url: str) -> Callable[[T], T]:
    """Connect a problem to a Gradescope assignment.

    :param url: The url of the Gradescope assignment.
    """


def gs_connect[T: Problem](
    url_or_cid: str,
    aid: str | None = None,
) -> Callable[[T], T]:
    """Connect a problem to a Gradescope assignment.

    :param url_or_cid: The course id of the Gradescope assignment, or the url when aid is not specified.
        The format of the url should be
        https://www.gradescope.com/courses/<cid>/assignments/<aid>[anything]

            connect('12443', '112358')  # specify cid and aid
            connect('https://www.gradescope.com/courses/12443/assignments/112358')  # specify url

    :param aid: The assignment id of the Gradescope assignment.

    """
    gs_connect_config = build_connect_config(url_or_cid, aid)

    def _wrapper(prob: T) -> T:
        prob.config.extras["gs_connect"] = gs_connect_config
        return prob

    return _wrapper
