"""Command line interface for checking the problem against the gap_check fields."""
import typer

from gapper.cli.cli_options import (
    AutoInjectOpt,
    InjectOpt,
    ProblemPathArg,
    VerboseOpt,
    timed,
)
from gapper.cli.rich_test_check_output import rich_print_test_check
from gapper.cli.utils import cli_logger, setup_root_logger
from gapper.core.injection import InjectionHandler
from gapper.core.problem import Problem


@timed
def check(
    path: ProblemPathArg,
    auto_inject: AutoInjectOpt,
    inject: InjectOpt,
    verbose: VerboseOpt = False,
) -> None:
    """Check if the problem is defined correctly again the gap_check fields."""
    setup_root_logger(verbose)

    InjectionHandler().setup(auto_inject, inject).inject()
    cli_logger.debug("Injection setup")

    problem = Problem.from_path(path)
    cli_logger.debug("Problem loaded")

    cli_logger.debug("Start test checking")
    try:
        for test in problem.generate_tests():
            checked_result = test.check_test()
            rich_print_test_check(
                test.test_param.format(),
                checked_result,
                (
                    test.test_param.param_info.gap_expect,
                    test.test_param.param_info.gap_expect_stdout,
                ),
            )
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)
