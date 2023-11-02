from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List, Protocol, Self

from gapper.core.errors import InternalError
from gapper.core.test_result import TestResult
from gapper.gradescope.datatypes.gradescope_output import GradescopeJson

if TYPE_CHECKING:
    from gapper.core.problem import Problem
    from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata


class PostTestFn(Protocol):
    def __call__(
        self, synthesizer: ResultSynthesizer, result_proxy: TestResult | None
    ) -> None:
        ...


class PostTest:
    def __init__(self, post_test_fn: PostTestFn, as_test_case: bool = True) -> None:
        self.post_test_fn = post_test_fn
        self.as_test_case = as_test_case

    def __call__(self, problem: Problem) -> Problem:
        problem.add_post_test(self)
        return problem


class ResultSynthesizer:
    def __init__(
        self,
        *,
        results: List[TestResult] = None,
        post_tests: List[PostTest] = None,
        metadata: GradescopeSubmissionMetadata | None = None,
        total_score: float | None = None,
    ) -> None:
        self._results: List[TestResult] = results or []
        self._post_tests: List[PostTest] = post_tests or []
        self._metadata = metadata
        self._total_score = total_score

    @property
    def metadata(self):
        return self._metadata

    @property
    def total_score(self) -> float:
        if self._metadata is None and self._total_score is None:
            raise ValueError("metadata and total_score are not set")

        if self._metadata is not None:
            return self._metadata.assignment.total_points
        else:
            return self._total_score

    def run_post_tests(self) -> Self:
        for post_test in self._post_tests:
            if post_test.as_test_case:
                result_proxy = TestResult(post_test.post_test_fn.__name__)
            else:
                result_proxy = None
            post_test.post_test_fn(self, result_proxy)

            if result_proxy is not None:
                self._results.append(result_proxy)

        return self

    def synthesize_score(self) -> float:
        results_with_score = []
        results_with_weight = []

        max_score_sum = 0.0
        weight_sum = 0

        for res in self._results:
            if res.max_score is None and res.weight is None:
                raise InternalError(
                    "The max_score and weight of a test (result) cannot both be None."
                )

            if res.max_score is not None and res.weight is not None:
                raise InternalError(
                    "The max_score and weight of a test (result) cannot both be set."
                )

            if res.max_score is not None:
                results_with_score.append(res)
                max_score_sum += res.max_score
            elif res.weight is not None:
                results_with_weight.append(res)
                weight_sum += res.weight
            else:
                raise InternalError(
                    f"The max_score and weight of a test (result) cannot both be None, "
                    f"but {res.rich_test_name} has both being None."
                )

        if max_score_sum > self.total_score:
            raise InternalError(
                f"The sum of the scores ({max_score_sum}) of all tests must be less than or equal to the "
                f"total points for the assignment ({self.total_score}). This does not apply to the gap_extra_points."
            )

        remaining_score = self.total_score - max_score_sum

        for res in results_with_weight:
            assert res.weight is not None
            res.max_score = res.weight * remaining_score / weight_sum
            res.weight = None

        for res in self._results:
            if res.score is not None:
                if res.score < 0:
                    raise InternalError(
                        f"Test {res.name} has a negative score ({res.score})."
                    )

                if res.extra_points is not None:
                    raise InternalError(
                        f"In test ({res.name}) extra score is ignored because a score is set through custom test check."
                    )

                continue

            assert res.max_score is not None

            # interpret score with pass status
            if res.pass_status == "passed":
                res.score = (
                    res.max_score + 0 if res.extra_points is None else res.extra_points
                )
            else:
                res.score = 0

        return sum((res.score for res in self._results), 0.0)

    def to_gradescope_json(
        self, save_path: Path | None = None, **kwargs
    ) -> GradescopeJson:
        score = self.run_post_tests().synthesize_score()
        return GradescopeJson.from_test_results(
            self._results, score, save_path, **kwargs
        )
