from pathlib import Path
from typing import List, Any

import pytest

from gap.core.tester import Tester
from tests.conftest import preset_problem_paths, TEST_SUBMISSIONS_FOLDER


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
