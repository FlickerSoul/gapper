import logging
from pathlib import Path
from typing import Annotated, List, Optional

import typer

from gapper.cli.rich_test_check_output import rich_print_test_check
from gapper.cli.rich_test_result_output import rich_print_test_results
from gapper.core.file_handlers import AutograderZipper
from gapper.core.injection import InjectionHandler
from gapper.core.problem import Problem
from gapper.core.result_synthesizer import ResultSynthesizer
from gapper.core.tester import Tester
from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata
from gapper.gradescope.main import run_autograder
from gapper.gradescope.vars import (
    AUTOGRADER_METADATA,
    AUTOGRADER_OUTPUT,
    AUTOGRADER_SUBMISSION,
    AUTOGRADER_TESTER_PICKLE,
)
from gapper.logger_utils import setup_root_logger

app = typer.Typer()

cli_logger = logging.getLogger("gapper.cli")

ProblemPathArg = Annotated[
    Path, typer.Argument(help="The path to the problem python file.")
]
SubmissionPathArg = Annotated[
    Path, typer.Argument(help="The path to the submission file.")
]
TesterConfigPathOpt = Annotated[
    Path,
    typer.Option(
        "--config",
        "-c",
        help="The path to the tester config file.",
        default_factory=lambda: Path.cwd() / "default.toml",
        dir_okay=False,
    ),
]
SavePathOpt = Annotated[
    Path,
    typer.Option(
        "--save-path",
        "-s",
        help="The directory to save the generated tester file.",
        default_factory=lambda: Path.cwd(),
        file_okay=False,
    ),
]
VerboseOpt = Annotated[
    bool,
    typer.Option(
        "--verbose",
        "-v",
        help="Whether to run in verbose mode.",
    ),
]
MetadataOpt = Annotated[
    Optional[Path],
    typer.Option(
        "--metadata",
        "-m",
        help="The path to the submission metadata file.",
        default_factory=lambda: None,
        dir_okay=False,
    ),
]
AutoInjectOpt = Annotated[
    bool,
    typer.Option(
        "--auto-inject",
        "-a",
        help="Whether to auto inject the tester file.",
        default_factory=lambda: False,
    ),
]
InjectOpt = Annotated[
    List[Path],
    typer.Option(
        "--inject",
        "-i",
        help="The path to the tester file to inject.",
        default_factory=list,
    ),
]


@app.command()
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


@app.command()
def gen(
    path: ProblemPathArg,
    save_path: SavePathOpt,
    auto_inject: AutoInjectOpt,
    inject: InjectOpt,
    verbose: VerboseOpt = False,
) -> None:
    """Generate the autograder for a problem."""
    setup_root_logger(verbose)

    InjectionHandler().setup(auto_inject, inject).inject()
    cli_logger.debug("Injection setup")

    problem = Problem.from_path(path)
    cli_logger.debug("Problem loaded")

    tester = Tester(problem)
    cli_logger.debug("Tester generated from problem")

    AutograderZipper(tester).generate_zip(
        save_path / f"{problem.expected_submission_name}.zip"
    )
    cli_logger.debug("Autograder zip generated")


@app.command()
def run(
    path: ProblemPathArg,
    submission: SubmissionPathArg,
    metadata_path: MetadataOpt,
    auto_inject: AutoInjectOpt,
    inject: InjectOpt,
    verbose: VerboseOpt = False,
    total_score: float = 20,
) -> None:
    """Run the autograder on an example submission."""
    setup_root_logger(verbose)

    cli_logger.debug(
        f"Try loading metadata from {metadata_path and metadata_path.absolute()}"
    )
    metadata = (
        None
        if metadata_path is None
        else GradescopeSubmissionMetadata.from_file(metadata_path)
    )
    cli_logger.debug(f"Metadata loaded: {metadata}")

    total_score = metadata.assignment.total_points if metadata else total_score
    cli_logger.debug(f"Total score is set to: {total_score}")

    InjectionHandler().setup(auto_inject, inject).inject()
    cli_logger.debug("Injection setup")

    problem = Problem.from_path(path)
    cli_logger.debug("Problem loaded")

    tester = Tester(problem)
    cli_logger.debug("Tester generated from problem")

    test_results = tester.load_submission_from_path(submission).run(metadata)
    cli_logger.debug("Test results generated from tester")

    score_obtained = (
        ResultSynthesizer(
            results=test_results, post_tests=problem.post_tests, total_score=total_score
        )
        .run_post_tests()
        .synthesize_score()
    )
    cli_logger.debug(f"Score obtained from synthesizer {score_obtained}")

    rich_print_test_results(test_results, score_obtained, total_score)


@app.command()
def run_in_prod(
    tester_path: Annotated[
        Path,
        typer.Argument(help="The path to the tester pickle file."),
    ] = AUTOGRADER_TESTER_PICKLE,
    submission_dir: Annotated[
        Path,
        typer.Argument(help="The path to the submission directory."),
    ] = AUTOGRADER_SUBMISSION,
    metadata_file: Annotated[
        Path,
        typer.Argument(
            help="The path to the submission metadata file.",
        ),
    ] = AUTOGRADER_METADATA,
    output_file: Annotated[
        Path,
        typer.Argument(help="The path to the output file."),
    ] = AUTOGRADER_OUTPUT,
    verbose: VerboseOpt = False,
) -> None:
    """Run the autograder in production mode."""
    setup_root_logger(verbose)

    cli_logger.debug("Autograder run in production mode")
    run_autograder(tester_path, submission_dir, metadata_file, output_file)
    cli_logger.debug("Autograder run finished")


__all__ = ["app"]
