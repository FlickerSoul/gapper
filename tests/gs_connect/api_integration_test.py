import asyncio
import re

import pytest
from gapper.connect.api.account import GSAccount

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
