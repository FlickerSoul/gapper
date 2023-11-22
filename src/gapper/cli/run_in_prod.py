"""CLI command to run the autograder in production mode."""
from pathlib import Path
from typing import Annotated

import typer

from gapper.cli.cli_options import VerboseOpt, timed
from gapper.cli.utils import cli_logger, setup_root_logger
from gapper.gradescope.main import run_autograder
from gapper.gradescope.vars import (
    AUTOGRADER_METADATA,
    AUTOGRADER_OUTPUT,
    AUTOGRADER_SUBMISSION,
    AUTOGRADER_TESTER_PICKLE,
)


@timed
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
    verbose: VerboseOpt = True,
) -> None:
    """Run the autograder in production mode."""
    setup_root_logger(verbose)

    cli_logger.debug("Autograder run in production mode")
    run_autograder(tester_path, submission_dir, metadata_file, output_file)
    cli_logger.debug("Autograder run finished")
