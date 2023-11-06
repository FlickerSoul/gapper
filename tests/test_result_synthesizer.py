import re

import pytest

from gapper.core.errors import InternalError
from gapper.core.result_synthesizer import ResultSynthesizer
from gapper.core.test_result import TestResult


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


def test_invalid_total_score() -> None:
    with pytest.raises(ValueError, match="metadata and total_score are not set"):
        _ = ResultSynthesizer().total_score


def test_synthesize_score_with_weight() -> None:
    results = [
        TestResult("dummy test", max_score=1, pass_status="passed"),
        TestResult("dummy test", max_score=1, pass_status="passed"),
        TestResult("dummy test", weight=2, pass_status="passed"),
        TestResult("dummy test", weight=3, pass_status="passed"),
    ]

    expected_max_scores = [1, 1, 0.8, 1.2]

    total_score = sum(expected_max_scores)

    assert (
        ResultSynthesizer.synthesize_score_for(results=results, total_score=total_score)
        == total_score
    )

    assert all(
        result.max_score == score for result, score in zip(results, expected_max_scores)
    )


def test_extra_points_added() -> None:
    results = [
        TestResult("dummy test", max_score=1, pass_status="passed", extra_points=3),
    ]

    assert ResultSynthesizer.synthesize_score_for(results=results, total_score=1) == 4

    results = [
        TestResult(
            "dummy test", score=0, max_score=1, pass_status="passed", extra_points=3
        ),
    ]

    assert ResultSynthesizer.synthesize_score_for(results=results, total_score=1) == 3
