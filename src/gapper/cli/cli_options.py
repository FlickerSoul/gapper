"""CLI options for gapper."""
from functools import wraps
from pathlib import Path
from time import time
from typing import Annotated, List, Optional

import typer

from gapper.cli.utils import cli_logger

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
UIDebugOpt = Annotated[
    bool,
    typer.Option(
        "--ui-debug",
        "-d",
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
OverwriteConfirmOpt = Annotated[
    bool,
    typer.Option(
        "--confirm-overwrite",
        "-y",
        is_flag=True,
        help="Confirm overwrite files.",
    ),
]
UploadOpt = Annotated[
    bool,
    typer.Option(
        "--upload", "-u", is_flag=True, help="Whether to upload the autograder."
    ),
]
UseGUIOpt = Annotated[
    bool,
    typer.Option(
        "--gui",
        "-g",
        is_flag=True,
        help="Whether to use the GUI to upload.",
    ),
]
LoginSavePath = Annotated[
    Path,
    typer.Option(
        "--login-save-path",
        "-l",
        dir_okay=False,
        help="The path to save the login info.",
    ),
]


def timed[T](fn: T) -> T:
    """Time a function execution."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time()
        result = fn(*args, **kwargs)
        end = time()
        cli_logger.debug(f"Time elapsed: {end - start}s")
        return result

    return wrapper
