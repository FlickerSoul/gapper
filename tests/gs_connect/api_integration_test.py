import asyncio
import re
from pathlib import Path

import pytest
from gapper.cli import app as cli_app
from gapper.connect.api.account import GSAccount
from typer.testing import CliRunner

from tests.gs_connect.conftest import AccountDetail


def test_account_login(gs_account: AccountDetail) -> None:
    account = GSAccount(*gs_account).spawn_session()
    asyncio.run(account.login())


def test_login_failed(gs_dummy_account: AccountDetail) -> None:
    account = GSAccount(*gs_dummy_account).spawn_session()
    with pytest.raises(ValueError, match=re.escape("Login failed")):
        asyncio.run(account.login())


def test_account_login_with_cookie(gs_account: AccountDetail) -> None:
    account = GSAccount(*gs_account).spawn_session()
    asyncio.run(account.login())
    account.password = None
    asyncio.run(account.login())


def test_cli_login(gs_account: AccountDetail, tmp_path: Path) -> None:
    login_save = tmp_path / "login_save.json"
    args = ["login", "-l", str(login_save.absolute())]
    result = CliRunner().invoke(
        cli_app, args, input="".join(map(lambda x: x + "\n", gs_account))
    )
    assert result.exit_code == 0


def test_cli_login_failed(gs_dummy_account: AccountDetail, tmp_path: Path) -> None:
    login_save = tmp_path / "login_save.json"
    args = ["login", "-l", str(login_save.absolute())]
    result = CliRunner().invoke(
        cli_app, args, input="".join(map(lambda x: x + "\n", gs_dummy_account))
    )
    assert result.exit_code == 1
