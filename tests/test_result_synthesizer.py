import pytest

from gapper.core.problem import Problem
from gapper.core.result_synthesizer import ResultSynthesizer
from gapper.core.test_result import TestResult
from tests.conftest import _make_problem_name


def test_post_test(request: pytest.FixtureRequest) -> None:
    problem: Problem = request.getfixturevalue(
        _make_problem_name("assess_post_tests.py")
    )
    results = [
        TestResult("test result", pass_status="passed", max_score=1, score=1)
        for _ in range(10)
    ]
    old_len = len(results)
    old_score = sum(result.score for result in results)
    syn = ResultSynthesizer(
        results=results, post_tests=problem.post_tests, total_score=10
    ).run_post_tests()

    assert len(results) == old_len + 1
    assert syn.synthesize_score() == old_score + 5
