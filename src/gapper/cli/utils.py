"""Utility functions for CLI commands."""
import asyncio
import logging
import traceback
from pathlib import Path

import typer

from gapper.connect.api.account import GSAccount
from gapper.connect.api.assignment import GSAssignmentEssential
from gapper.connect.gui.app_ui import GradescopeConnect
from gapper.connect.gui.upload_app_ui import AutograderUploadApp

_package_logger = logging.getLogger("gapper")
cli_logger = logging.getLogger("gapper.cli")


def load_account_from_path(login_save_path: Path) -> GSAccount:
    """Load the account cookie login info from the given path.

    :param login_save_path: The path to the login save file.
    """
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
    """Check if the login is valid.

    :param account: The account to check.
    """
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
    """Upload the autograder with GUI.

    :param login_save_path: The path to the login save file.
    :param autograder_path: The path to the autograder zip file.
    """
    gs_app = GradescopeConnect(
        login_save_path=login_save_path, autograder_path=autograder_path
    )
    gs_app.run()


def upload_with_connect_details(
    cid: str, aid: str, login_save_path: Path, autograder_path: Path
) -> None:
    """Upload the autograder with connect details.

    :param cid: The course id.
    :param aid: The assignment id.
    :param login_save_path: The path to the login save file.
    :param autograder_path: The path to the autograder zip file.
    """
    account = load_account_from_path(login_save_path)
    check_login_valid(account)

    gs_assignment = GSAssignmentEssential(cid, aid, session=account.session)
    gs_app = AutograderUploadApp(
        assignment=gs_assignment, autograder_path=autograder_path
    )
    gs_app.run()


def setup_root_logger(verbose: bool) -> None:
    """Set up the root logger.

    :param verbose: Whether to run in verbose mode.
    """
    level = logging.DEBUG if verbose else logging.INFO
    _package_logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    # add formatter to ch
    ch.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # add ch to logger
    _package_logger.addHandler(ch)

    _package_logger.debug(f"Set up root logger with level {level}.")
