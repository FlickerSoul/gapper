from pathlib import Path
from typing import Annotated, Optional

import typer

from gapper.cli.cli_options import LoginSavePath, UIDebugOpt, UseGUIOpt, timed
from gapper.cli.utils import upload_with_connect_details, upload_with_gui
from gapper.connect.gui.utils import DEFAULT_LOGIN_SAVE_PATH, add_debug_to_app
from gapper.core.problem import build_connect_config


@timed
def upload(
    autograder_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            help="The path to the autograder zip file.",
        ),
    ],
    use_ui: UseGUIOpt = False,
    login_save_path: LoginSavePath = DEFAULT_LOGIN_SAVE_PATH,
    url: Annotated[
        Optional[str], typer.Option("--url", "-u", help="The url to the autograder.")
    ] = None,
    cid: Annotated[
        Optional[str], typer.Option("--cid", "-c", help="The course id.")
    ] = None,
    aid: Annotated[
        Optional[str], typer.Option("--aid", "-a", help="The assignment id.")
    ] = None,
    ui_debug: UIDebugOpt = False,
) -> None:
    """Upload an autograder to Gradescope."""
    add_debug_to_app(ui_debug)

    if use_ui:
        upload_with_gui(login_save_path, autograder_path)
    else:
        if url:
            typer.echo("Using url to upload. Ignoring cid and aid.")
            connect_config = build_connect_config(url)
        else:
            typer.echo("Using cid and aid to upload.")
            connect_config = build_connect_config(cid, aid)

        upload_with_connect_details(
            connect_config.cid, connect_config.aid, login_save_path, autograder_path
        )
