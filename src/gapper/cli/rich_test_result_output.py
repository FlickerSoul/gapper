"""Rich test result output."""
from __future__ import annotations

from typing import TYPE_CHECKING, List

from rich import print as rprint
from rich.box import ROUNDED
from rich.panel import Panel

if TYPE_CHECKING:
    from gapper.core.test_result import TestResult


RICH_PANEL_OPTS = {
    "box": ROUNDED,
    "title_align": "left",
    "subtitle_align": "right",
}


def rich_print_test_results(
    results: List[TestResult],
    score_obtained: float,
    total_score: float,
) -> None:
    """Print a fancy summary of the problem.

    :param results: The results of the problem.
    :param score_obtained: The score obtained by the submissions.
    :param total_score: The total score of all tests.
    """
    rprint(
        Panel(
            "The following is the test results.",
            title="Overall",
            subtitle=f"{score_obtained}/{total_score} | Score Obtained/Total score",
            **RICH_PANEL_OPTS,  # type: ignore
        )
    )

    for result in results:
        rprint(
            Panel(
                result.rich_test_output,
                title=("" if result.is_passed else "[bright_red]")
                + ("(HIDDEN) " if result.hidden else "")
                + result.rich_test_name,
                subtitle=f"{result.score}/{result.max_score}",
                **RICH_PANEL_OPTS,  # type: ignore
            )
        )
