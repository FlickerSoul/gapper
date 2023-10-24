from pathlib import Path
from typing import Annotated, List, Optional

import typer

from gapper.cli.test_result_output import rich_print_test_results
from gapper.core.file_handlers import AutograderZipper
from gapper.core.injection import InjectionHandler
from gapper.core.problem import Problem
from gapper.core.tester import Tester
from gapper.gradescope import run_autograder
from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata
from gapper.gradescope.datatypes.gradescope_output import GradescopeJson
from gapper.gradescope.vars import (
    AUTOGRADER_METADATA,
    AUTOGRADER_OUTPUT,
    AUTOGRADER_SUBMISSION,
    AUTOGRADER_TESTER_PICKLE,
)

app = typer.Typer()

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
DebugOpt = Annotated[
    bool,
    typer.Option(
        "--debug",
        "-d",
        help="Whether to run in debug mode.",
        default_factory=lambda: False,
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
    ),
]


@app.command()
def check(
    path: ProblemPathArg,
    debug: DebugOpt,
    auto_inject: AutoInjectOpt,
    inject: InjectOpt,
) -> None:
    InjectionHandler().setup(auto_inject, inject).inject()

    problem = Problem.from_path(path)
    try:
        for test in problem.generate_tests():
            pass_flag = test.check_test()
            test_desc = (
                f"skipped due to no expect"
                if pass_flag is None
                else f"passed: {pass_flag}"
            )
            typer.echo(f"Test {test.test_param.format()} {test_desc}")
    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def gen(
    path: ProblemPathArg,
    save_path: SavePathOpt,
    auto_inject: AutoInjectOpt,
    inject: InjectOpt,
    debug: DebugOpt,
) -> None:
    InjectionHandler().setup(auto_inject, inject).inject()

    problem = Problem.from_path(path)
    tester = Tester(problem)
    AutograderZipper(tester).generate_zip(
        save_path / f"{problem.expected_submission_name}.zip"
    )


@app.command()
def run(
    path: ProblemPathArg,
    submission: SubmissionPathArg,
    debug: DebugOpt,
    metadata_path: MetadataOpt,
    auto_inject: AutoInjectOpt,
    inject: InjectOpt,
    total_score: float = 20,
) -> None:
    """Run the autograder on an example submission."""
    metadata = (
        None
        if metadata_path is None
        else GradescopeSubmissionMetadata.from_file(metadata_path)
    )
    total_score = metadata.assignment.total_points if metadata else total_score
    InjectionHandler().setup(auto_inject, inject).inject()

    problem = Problem.from_path(path)
    tester = Tester(problem)
    test_results = tester.load_submission_from_path(submission).run(metadata)
    score_obtained = GradescopeJson.synthesize_score(test_results, total_score)
    rich_print_test_results(test_results, score_obtained, total_score)


@app.command()
def run_in_prod(
    debug: DebugOpt,
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
) -> None:
    run_autograder(tester_path, submission_dir, metadata_file, output_file)


__all__ = ["app"]
