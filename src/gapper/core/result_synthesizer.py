"""This module contains a class to synthesize the results from a tester."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, List

from gapper.core.errors import InternalError
from gapper.core.test_result import TestResult
from gapper.core.utils import PostTestFn
from gapper.gradescope.datatypes.gradescope_output import GradescopeJson

if TYPE_CHECKING:
    from gapper.core.problem import Problem
    from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata

__all__ = ["ResultSynthesizer", "PostTest", "post_test"]


class PostTest:
    """A decorator for post tests. Will be used as @post_test() decorator."""

    def __init__(self, post_test_fn: PostTestFn, as_test_case: bool = True) -> None:
        """A decorator for specifying post tests. Will be used as @post_test().

            from gapper import post_test, problem

            @post_test()
            @problem()
            ...

        :param post_test_fn: The function to be called after all tests are run.
        :param as_test_case: Whether to treat the post test as a test case.
            If this is set to True, the post test will incur a TestResult instance to be created
            and be added to the pool of all test results after the post testing phrase is completed.
            The test result will then be used to synthesize the score.

            If this is set to False, the post test will not incur a TestResult instance.
        """
        self.post_test_fn = post_test_fn
        self.as_test_case = as_test_case

    def __call__(self, problem: Problem) -> Problem:
        """Add the post test to the problem.

        :param problem: The problem to add the post test to.
        """
        problem.add_post_test(self)
        return problem

    def __repr__(self) -> str:
        return f"PostTest(post_test_fn={self.post_test_fn}, as_test_case={self.as_test_case})"


post_test = PostTest


class ResultSynthesizer:
    def __init__(
        self,
        *,
        results: List[TestResult] | None = None,
        metadata: GradescopeSubmissionMetadata | None = None,
        total_score: float | None = None,
    ) -> None:
        """A class to synthesize the results from a tester.

        :param results: The results of the tester.
        :param metadata: The metadata of the submission.
        :param total_score: The total score of the assignment.
        """
        self._results: List[TestResult] = results or []
        self._metadata = metadata
        self._total_score = total_score
        self._logger = logging.getLogger("ResultSynthesizer")
        self._logger.debug(
            f"ResultSynthesizer created with results with "
            f"total score {total_score}, "
            f"{len(self._results)} tests, "
            f"and metadata {metadata}"
        )

    @property
    def results(self) -> List[TestResult]:
        """The results of the tester."""
        return self._results

    @property
    def metadata(self):
        """The metadata of the submission."""
        return self._metadata

    @property
    def total_score(self) -> float:
        """The total score of the assignment."""
        if self._metadata is None and self._total_score is None:
            raise ValueError("metadata and total_score are not set")

        if self._metadata is not None:
            return self._metadata.assignment.total_points
        else:
            return self._total_score

    @staticmethod
    def synthesize_score_for(*, results: List[TestResult], total_score: float) -> float:
        """Synthesize the score from the results.

        :param results: The results to synthesize the score from.
        :param total_score: The total score of the assignment.
        """
        results_with_score = []
        results_with_weight = []

        max_score_sum = 0.0
        weight_sum = 0

        for res in results:
            if res.max_score is not None and res.weight is not None:
                raise InternalError(
                    "The max_score and weight of a test (result) cannot both be set. "
                    f"But {res.rich_test_name} has both being None."
                )

            if res.max_score is not None:
                results_with_score.append(res)
                max_score_sum += res.max_score
            elif res.weight is not None:
                results_with_weight.append(res)
                weight_sum += res.weight
            else:
                raise InternalError(
                    f"The max_score and weight of a test (result) cannot both be None. "
                    f"But {res.rich_test_name} has both being None."
                )

        if max_score_sum > total_score:
            raise InternalError(
                f"The sum of the scores ({max_score_sum}) of all tests must be less than or equal to the "
                f"total points for the assignment ({total_score}). This does not apply to the gap_extra_points."
            )

        remaining_score = total_score - max_score_sum

        for res in results_with_weight:
            assert res.weight is not None
            res.max_score = res.weight * remaining_score / weight_sum
            res.weight = None

        for res in results:
            if res.score is not None:
                if res.score < 0:
                    raise InternalError(
                        f"Test {res.rich_test_name} has a negative score ({res.score})."
                    )

                if res.is_passed and res.extra_points is not None:
                    res.score += res.extra_points
            else:
                assert (
                    res.max_score is not None
                ), f"TestResult has to have max_score set, but {res.rich_test_name} does not."

                # interpret score with pass status
                if res.pass_status == "passed":
                    res.score = res.max_score + (
                        0 if res.extra_points is None else res.extra_points
                    )
                else:
                    res.score = 0

        return sum((res.score for res in results), 0.0)

    def synthesize_score(self) -> float:
        """Synthesize the score from the results."""
        return type(self).synthesize_score_for(
            results=self._results, total_score=self.total_score
        )

    def to_gradescope_json(
        self, save_path: Path | None = None, **kwargs
    ) -> GradescopeJson:
        """Convert the results to Gradescope JSON.

        :param save_path: The path to save the Gradescope JSON to.
        :param kwargs: The keyword arguments to pass to the GradescopeJson constructor.
        """
        self._logger.debug("Converting results to Gradescope JSON")
        score = self.synthesize_score()
        self._logger.debug(f"Score obtained: {score} | Total score: {self.total_score}")

        return GradescopeJson.from_test_results(
            self._results, score, save_path, **kwargs
        )
