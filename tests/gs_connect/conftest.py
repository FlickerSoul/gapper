import os
from typing import NamedTuple

import pytest

_not_set = object()


class AccountDetail(NamedTuple):
    email: str
    password: str


@pytest.fixture(scope="module")
def gs_email() -> str | object:
    return os.environ.get("GS_TEST_CONNECT_EMAIL", _not_set)


@pytest.fixture(scope="module")
def gs_password() -> str | object:
    return os.environ.get("GS_TEST_CONNECT_PASSWORD", _not_set)


@pytest.fixture(scope="module")
def gs_test_cid() -> str | object:
    return os.environ.get("GS_TEST_CONNECT_CID", _not_set)


@pytest.fixture(scope="module")
def gs_test_aid() -> str | object:
    return os.environ.get("GS_TEST_CONNECT_AID", _not_set)


@pytest.fixture(scope="module")
def gs_dummy_account() -> AccountDetail:
    return AccountDetail("dummy_email@icloud.com", "dummy_password")


@pytest.fixture(scope="class")
def gs_account(gs_email, gs_password) -> AccountDetail:
    if gs_password is _not_set or gs_email is _not_set:
        pytest.skip("GS Connect API Account test ENV variables are not set.")

    return AccountDetail(gs_email, gs_password)


@pytest.fixture()
def gs_cid(gs_test_cid) -> str:
    if gs_test_cid is _not_set:
        pytest.skip("GS Connect API Course ID test ENV variables are not set.")

    return gs_test_cid


@pytest.fixture()
def gs_aid(gs_test_aid) -> str:
    if gs_test_aid is _not_set:
        pytest.skip("GS Connect API Assignment ID test ENV variables are not set.")

    return gs_test_aid
