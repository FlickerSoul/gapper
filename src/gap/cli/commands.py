from pathlib import Path

import typer
from typing import Annotated

from gap.core.file_handlers import AutograderZipper
from gap.core.problem import Problem
from gap.core.tester import Tester, TesterConfig

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


@app.command()
def gen(
    path: ProblemPathArg,
    config: TesterConfigPathOpt,
    save_path: SavePathOpt,
    debug: DebugOpt,
) -> None:
    problem = Problem.from_file(path)
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
    save_path: SavePathOpt,
    debug: DebugOpt,
    sim_env: bool = False,
) -> None:
    problem = Problem.from_file(path)
    tester_config = TesterConfig.from_toml(config)
    tester = Tester(problem, config=tester_config)
    tester.load_submission_from_path(submission).run()
    # TODO: metadata sim
    # TODO: typer generate rich output


__all__ = ["app"]
