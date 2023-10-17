from pathlib import Path
from typing import Any

import pytest

from gapper.core.problem import Problem
from gapper.core.errors import NoSubmissionError, MultipleSubmissionError, InternalError
from gapper.core.tester import Tester
from tests.conftest import (
    preset_problem_paths,
    TEST_SUBMISSIONS_FOLDER,
    _make_problem_name,
    SINGLE_SUBMISSION_FOLDER,
    NO_SUBMISSION_FOLDER,
    MULTIPLE_SUBMISSIONS_FOLDER,
)


@pytest.mark.parametrize(
    "tester_fixture, path",
    (pytest.param(p, p, id=p.name) for p in preset_problem_paths()),
    indirect=["tester_fixture"],
)
def test_tester_run(tester_fixture: Tester[Any, Any], path: Path) -> None:
    submission_path = TEST_SUBMISSIONS_FOLDER / path.name

    for test_result in tester_fixture.load_submission_from_path(submission_path).run():
        assert test_result.errors == []
        assert test_result.pass_status == "passed"


def test_load_submission(request: pytest.FixtureRequest) -> None:
    prob = request.getfixturevalue(_make_problem_name("tester_submission.py"))
    tester = Tester(problem=prob)

    # the following two should run ok
    tester.load_submission_from_path(SINGLE_SUBMISSION_FOLDER)
    tester.load_submission_from_path(SINGLE_SUBMISSION_FOLDER / "tester_submission.py")


def test_no_submission_loading_error(request: pytest.FixtureRequest) -> None:
    prob = request.getfixturevalue(_make_problem_name("tester_submission.py"))
    tester = Tester(problem=prob)

    # the following two should run ok
    with pytest.raises(NoSubmissionError):
        tester.load_submission_from_path(NO_SUBMISSION_FOLDER)


def test_multiple_submissions_loading_error(request: pytest.FixtureRequest) -> None:
    prob = request.getfixturevalue(_make_problem_name("tester_submission.py"))
    tester = Tester(problem=prob)

    # the following two should run ok
    with pytest.raises(MultipleSubmissionError):
        tester.load_submission_from_path(MULTIPLE_SUBMISSIONS_FOLDER)


def test_no_problem_internal_error() -> None:
    with pytest.raises(InternalError, match="No problem loaded."):
        Tester(None).run()  # type: ignore


def test_no_submission_internal_error() -> None:
    with pytest.raises(InternalError, match="No submission loaded."):
        Tester(Problem(lambda: None, config=None)).run()  # type: ignore
