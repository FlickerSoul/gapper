from pathlib import Path
from typing import Any

import pytest
from gapper.core.errors import InternalError, MultipleSubmissionError, NoSubmissionError
from gapper.core.problem import Problem
from gapper.core.tester import Tester

from tests.conftest import (
    MULTIPLE_SUBMISSIONS_FOLDER,
    NO_SUBMISSION_FOLDER,
    SINGLE_SUBMISSION_FOLDER,
    TEST_SUBMISSIONS_FOLDER,
    make_problem_name,
    make_tester_name,
    preset_problem_paths,
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
    prob = request.getfixturevalue(make_problem_name("tester_submission.py"))
    tester = Tester(problem=prob)

    # the following two should run ok
    tester.load_submission_from_path(SINGLE_SUBMISSION_FOLDER)
    tester.load_submission_from_path(SINGLE_SUBMISSION_FOLDER / "tester_submission.py")


def test_no_submission_loading_error(request: pytest.FixtureRequest) -> None:
    prob = request.getfixturevalue(make_problem_name("tester_submission.py"))
    tester = Tester(problem=prob)

    # the following two should run ok
    with pytest.raises(NoSubmissionError):
        tester.load_submission_from_path(NO_SUBMISSION_FOLDER)


def test_multiple_submissions_loading_error(request: pytest.FixtureRequest) -> None:
    prob = request.getfixturevalue(make_problem_name("tester_submission.py"))
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


@pytest.mark.parametrize(
    "tester_fixture, name",
    (pytest.param(p, p.name, id=p.name) for p in preset_problem_paths()),
    indirect=["tester_fixture"],
)
def test_dump_and_load(tmp_path: Path, tester_fixture: Tester, name: str) -> None:
    if tester_fixture.problem.config.is_script:
        pytest.skip("Cannot pickle script problems.")

    dump_file = tmp_path / f"{name}_tester.dump"
    tester_fixture.dump_to(dump_file)
    restored_tester = Tester.from_file(dump_file)
    assert restored_tester.submission_context.keys() == tester_fixture.submission_context.keys()


def test_post_test(request: pytest.FixtureRequest) -> None:
    prob_name = "assess_post_tests.py"
    tester: Tester = request.getfixturevalue(make_tester_name(prob_name))
    results = tester.load_submission_from_path(TEST_SUBMISSIONS_FOLDER / prob_name).run()
    assert len(tester.problem.test_cases) + len(tester.problem.post_tests) == len(results)
