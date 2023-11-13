import asyncio
import logging
import traceback
from pathlib import Path

import typer

from gapper.connect.api.account import GSAccount
from gapper.connect.api.assignment import GSAssignmentEssential
from gapper.connect.gui.app_ui import GradescopeConnect
from gapper.connect.gui.upload_app_ui import AutograderUploadApp


def load_account_from_path(login_save_path: Path) -> GSAccount:
    try:
        account = GSAccount.from_yaml(login_save_path).spawn_session()
    except Exception as e:
        typer.secho(
            typer.style(
                f"Cannot load login info due to error {e}.\n"
                + "".join(traceback.format_tb(e.__traceback__)),
                fg=typer.colors.RED,
                bold=True,
            )
        )
        typer.echo("Please check your login save path.")
        typer.echo("If you haven't logged in, please use the login command.")
        raise typer.Exit(code=1)

    return account


def check_login_valid(account: GSAccount) -> None:
    try:
        asyncio.run(account.login(remember_me=True))
    except Exception as e:
        typer.secho(
            typer.style(
                f"Cannot login due to error {e}.\n"
                + "".join(traceback.format_tb(e.__traceback__)),
                fg=typer.colors.RED,
                bold=True,
            )
        )
        typer.echo("Please check your login info.")
        raise typer.Exit(code=1)


def upload_with_gui(login_save_path: Path, autograder_path: Path) -> None:
    gs_app = GradescopeConnect(
        login_save_path=login_save_path, autograder_path=autograder_path
    )
    gs_app.run()


def upload_with_connect_details(
    cid: str, aid: str, login_save_path: Path, autograder_path: Path
) -> None:
    account = load_account_from_path(login_save_path)
    check_login_valid(account)

    gs_assignment = GSAssignmentEssential(cid, aid, session=account.session)
    gs_app = AutograderUploadApp(
        assignment=gs_assignment, autograder_path=autograder_path
    )
    gs_app.run()


cli_logger = logging.getLogger("gapper.cli")
