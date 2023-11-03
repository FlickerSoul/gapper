import re

import pytest

from gapper.core.errors import InternalError
from gapper.core.problem import Problem
from gapper.core.result_synthesizer import ResultSynthesizer
from gapper.core.test_result import TestResult
from tests.conftest import _make_problem_name


def test_too_many_max_scores() -> None:
    results = [TestResult("dummy result", max_score=10)]
    with pytest.raises(InternalError, match="The sum of the scores"):
        ResultSynthesizer.synthesize_score_for(results=results, total_score=1)


def test_no_weight_and_max_score() -> None:
    results = [TestResult("dummy result")]
    with pytest.raises(
        InternalError,
        match=re.escape(
            "The max_score and weight of a test (result) cannot both be None."
        ),
    ):
        ResultSynthesizer.synthesize_score_for(results=results, total_score=1)


def test_both_weight_and_max_score() -> None:
    results = [TestResult("dummy result", max_score=1, weight=1)]
    with pytest.raises(
        InternalError,
        match=re.escape(
            "The max_score and weight of a test (result) cannot both be set."
        ),
    ):
        ResultSynthesizer.synthesize_score_for(results=results, total_score=1)


def test_not_allow_negative_score() -> None:
    results = [TestResult("dummy result", score=-1, max_score=1)]
    with pytest.raises(
        InternalError,
        match=re.escape("Test dummy result has a negative score (-1)."),
    ):
        ResultSynthesizer.synthesize_score_for(results=results, total_score=1)


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
