import os
from typing import NamedTuple

import pytest

_not_set = object()


class AccountDetail(NamedTuple):
    email: str
    password: str


@pytest.fixture(scope="module", autouse=True)
def ensure_gs_environment(gs_email, gs_password, gs_aid, gs_cid) -> None:
    test_connect_flag = os.environ.get("GS_TEST_CONNECT", _not_set)
    if test_connect_flag is _not_set or test_connect_flag != "ensure":
        return

    if any(value is _not_set for value in [gs_email, gs_password, gs_aid, gs_cid]):
        pytest.fail("GS Connect API test ENV variables are not set.")


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


@pytest.fixture(scope="module")
def gs_cid(gs_test_cid) -> str:
    if gs_test_cid is _not_set:
        pytest.skip("GS Connect API Course ID test ENV variables are not set.")

    return gs_test_cid


@pytest.fixture(scope="module")
def gs_aid(gs_test_aid) -> str:
    if gs_test_aid is _not_set:
        pytest.skip("GS Connect API Assignment ID test ENV variables are not set.")

    return gs_test_aid
