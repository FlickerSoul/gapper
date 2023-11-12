import asyncio
import os
import re
from typing import NamedTuple

import pytest

from gapper.connect.api.account import GSAccount

_not_set = object()


class _AccountDetail(NamedTuple):
    email: str
    password: str


@pytest.fixture(scope="module", autouse=True)
def gs_email() -> str | object:
    return os.environ.get("GS_TEST_CONNECT_EMAIL", _not_set)


@pytest.fixture(scope="module", autouse=True)
def gs_password() -> str | object:
    return os.environ.get("GS_TEST_CONNECT_PASSWORD", _not_set)


@pytest.fixture(scope="module")
def gs_dummy_account() -> _AccountDetail:
    return _AccountDetail("dummy_email@icloud.com", "dummy_password")


class TestGSConnectAPI:
    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def gs_account(cls, gs_email, gs_password) -> _AccountDetail:
        if gs_password is _not_set or gs_email is _not_set:
            pytest.skip("GS Connect API test ENV variables are not set.")

        return _AccountDetail(gs_email, gs_password)

    def test_account_login(self, gs_account: _AccountDetail) -> None:
        account = GSAccount(*gs_account).spawn_session()
        asyncio.run(account.login())

    def test_login_failed(self, gs_dummy_account: _AccountDetail) -> None:
        account = GSAccount(*gs_dummy_account).spawn_session()
        with pytest.raises(ValueError, match=re.escape("Login failed")):
            asyncio.run(account.login())

    def test_account_login_with_cookie(self, gs_account: _AccountDetail) -> None:
        account = GSAccount(*gs_account).spawn_session()
        asyncio.run(account.login())
        account.password = None
        asyncio.run(account.login())
