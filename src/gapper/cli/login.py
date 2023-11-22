"""CLI command to login to Gradescope."""
from typing import Annotated

import typer

from gapper.cli.cli_options import (
    LoginSavePath,
    OverwriteConfirmOpt,
    VerboseOpt,
    timed,
)
from gapper.cli.utils import check_login_valid, setup_root_logger
from gapper.connect.api.account import GSAccount
from gapper.connect.gui.utils import DEFAULT_LOGIN_SAVE_PATH


@timed
def login(
    confirm_store: Annotated[
        bool,
        typer.Option(
            "--confirm-store",
            "-s",
            is_flag=True,
            help="Confirm storing your login info.",
        ),
    ] = False,
    confirm_overwrite: OverwriteConfirmOpt = False,
    login_save_path: LoginSavePath = DEFAULT_LOGIN_SAVE_PATH,
    verbose: VerboseOpt = False,
) -> None:
    """Login to Gradescope."""
    setup_root_logger(verbose)

    email = typer.prompt("Enter your gradescope email")
    password = typer.prompt("Enter your gradescope password", hide_input=True)
    account = GSAccount(email, password).spawn_session()
    check_login_valid(account)

    if confirm_store or typer.confirm(
        "Confirm you want to store your session?", default=True, abort=True
    ):
        if (
            not login_save_path.exists()
            or confirm_overwrite
            or typer.confirm(
                "File already exists. Overwrite?", default=False, abort=True
            )
        ):
            account.to_yaml(login_save_path)
            typer.echo(f"Login info saved to {login_save_path.absolute()}")
            return
