"""Rich print the test check result."""
from textwrap import indent
from typing import Any, Tuple

from rich import print as rprint
from rich.box import ROUNDED
from rich.panel import Panel

RICH_PANEL_OPTS = {
    "box": ROUNDED,
    "title_align": "left",
    "subtitle_align": "right",
}


def rich_print_test_check(
    param_info: str,
    test_check_result: Tuple[bool, Any, str | None] | None,
    expected_result: Tuple[Any, str | None],
) -> None:
    """Print the test check result.

    :param param_info: The parameter info of the test, serving as the title.
    :param test_check_result: The test check result.
    :param expected_result: The expected result of the test.
    """
    if test_check_result is None:
        test_desc = "Skipped due to no gap_expect or gap_expect_stdout"
    else:
        pass_flag, result, output = test_check_result
        gap_expect, gap_expect_stdout = expected_result
        test_desc = (
            "[bold green]Passed[/bold green]"
            if pass_flag
            else "[bold red]Failed[/bold red]"
        )
        if not pass_flag:
            test_desc += "\n" + indent(
                f"result: \n{indent(str(result), ' ' * 2)}\n"
                f"expected result: \n{indent(str(gap_expect), ' ' * 2)}",
                " " * 2,
            )
            test_desc += "\n" + indent(
                f"output: \n{indent(str(output), ' ' * 2)}\n"
                f"expected output: \n{indent(str(gap_expect_stdout), ' ' * 2)}",
                " " * 2,
            )

    rprint(
        Panel(
            test_desc,
            title=f"Checks {param_info}",
            **RICH_PANEL_OPTS,
        )
    )
