from pathlib import Path

import typer
from typing import Annotated, Optional

from gapper.cli.test_result_output import rich_print_test_results
from gapper.core.file_handlers import AutograderZipper
from gapper.core.problem import Problem
from gapper.core.tester import Tester, TesterConfig
from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata
from gapper.gradescope.datatypes.gradescope_output import GradescopeJson

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
    ),
]
SavePathOpt = Annotated[
    Path,
    typer.Option(
        "--save-path",
        "-s",
        help="The directory to save the generated tester file.",
        default_factory=lambda: Path.cwd(),
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
    ),
]


@app.command()
def gen(
    path: ProblemPathArg,
    config: TesterConfigPathOpt,
    save_path: SavePathOpt,
    debug: DebugOpt,
) -> None:
    problem = Problem.from_path(path)
    tester_config = TesterConfig.from_toml(config)
    tester = Tester(problem, config=tester_config)
    AutograderZipper(tester).generate_zip(
        save_path / f"{problem.expected_submission_name}.zip"
    )


@app.command()
def run(
    path: ProblemPathArg,
    submission: SubmissionPathArg,
    config: TesterConfigPathOpt,
    debug: DebugOpt,
    metadata_path: MetadataOpt,
    total_score: float = 20,
) -> None:
    """Run the autograder on an example submission."""
    problem = Problem.from_path(path)
    tester_config = TesterConfig.from_toml(config)
    metadata = (
        None
        if metadata_path is None
        else GradescopeSubmissionMetadata.from_file(metadata_path)
    )
    total_score = metadata.assignment.total_points if metadata else total_score

    tester = Tester(problem, config=tester_config)
    test_results = tester.load_submission_from_path(submission).run(metadata)
    score_obtained = GradescopeJson.synthesize_score(test_results, total_score)
    rich_print_test_results(test_results, score_obtained, total_score)


__all__ = ["app"]
