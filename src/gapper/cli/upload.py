"""Upload an autograder to Gradescope."""
from pathlib import Path
from typing import Annotated, Optional

import typer

from gapper.cli.cli_options import LoginSavePath, UIDebugOpt, timed
from gapper.cli.utils import upload_with_connect_details, upload_with_gui
from gapper.connect.gui.utils import DEFAULT_LOGIN_SAVE_PATH, add_debug_to_app
from gapper.core.problem.extras.gradescope_connect import build_connect_config

upload = typer.Typer(name="upload")


@upload.command()
@timed
def gui(
    autograder_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            help="The path to the autograder zip file.",
        ),
    ],
    login_save_path: LoginSavePath = DEFAULT_LOGIN_SAVE_PATH,
    ui_debug: UIDebugOpt = False,
) -> None:
    """Upload an autograder to Gradescope with GUI."""
    add_debug_to_app(ui_debug)
    upload_with_gui(login_save_path, autograder_path)


@upload.command()
@timed
def url(
    autograder_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            help="The path to the autograder zip file.",
        ),
    ],
    assignment_url: Annotated[
        Optional[str], typer.Argument(help="The url to the autograder.")
    ],
    login_save_path: LoginSavePath = DEFAULT_LOGIN_SAVE_PATH,
    ui_debug: UIDebugOpt = False,
) -> None:
    """Upload an autograder to Gradescope using the assignment url."""
    add_debug_to_app(ui_debug)

    typer.echo("Using url to upload. Ignoring cid and aid.")
    connect_config = build_connect_config(assignment_url)
    upload_with_connect_details(
        connect_config.cid, connect_config.aid, login_save_path, autograder_path
    )


@upload.command()
@timed
def ids(
    autograder_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            help="The path to the autograder zip file.",
        ),
    ],
    login_save_path: LoginSavePath = DEFAULT_LOGIN_SAVE_PATH,
    ui_debug: UIDebugOpt = False,
    cid: Annotated[Optional[str], typer.Argument(help="The course id.")] = None,
    aid: Annotated[Optional[str], typer.Argument(help="The assignment id.")] = None,
) -> None:
    """Upload an autograder to Gradescope using the cid and aid."""
    add_debug_to_app(ui_debug)

    typer.echo("Using cid and aid to upload.")
    connect_config = build_connect_config(cid, aid)

    upload_with_connect_details(
        connect_config.cid, connect_config.aid, login_save_path, autograder_path
    )
