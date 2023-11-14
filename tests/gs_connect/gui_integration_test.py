from __future__ import annotations

import os
from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator, cast
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from gapper.connect.api.assignment import GSAssignmentEssential
from gapper.connect.gui.app_ui import GradescopeConnect
from gapper.connect.gui.autograder_upload_ui import AutograderUpload
from gapper.connect.gui.course_assignment_ui import (
    CourseScreen,
    make_course_car_name,
)
from gapper.connect.gui.login_ui import LoginScreen
from gapper.connect.gui.upload_app_ui import AutograderUploadApp
from pytest_mock import MockerFixture
from rich.text import Text
from textual.widgets import DataTable, Input, Label
from textual.widgets.data_table import RowKey

from tests.conftest import PACKED_AUTOGRADER_FOLDER
from tests.gs_connect.conftest import AccountDetail

if TYPE_CHECKING:
    from textual.pilot import Pilot


@contextmanager
def suppress():
    with open(os.devnull, "w") as null:
        with redirect_stdout(null):
            yield


@pytest_asyncio.fixture()
async def main_app_pilot() -> AsyncGenerator[Pilot, None]:
    app = GradescopeConnect()
    async with app.run_test() as pilot:  # type: Pilot
        await pilot.pause()
        yield pilot


async def enter_account_detail(
    pilot: Pilot, account: AccountDetail, remember_me: bool = False
) -> None:
    with suppress():
        await pilot.click("#email_input")
        await pilot.press(*account.email)
        await pilot.click("#password_input")
        await pilot.press(*account.password)

    if remember_me:
        await pilot.click("#remember_me")


@pytest.mark.asyncio
async def test_login_gui(gs_account: AccountDetail, main_app_pilot: Pilot) -> None:
    await enter_account_detail(main_app_pilot, gs_account)

    await main_app_pilot.click("#login_btn")

    await main_app_pilot.pause()

    assert isinstance(main_app_pilot.app.screen, CourseScreen)


@pytest.mark.asyncio
async def test_login_save(gs_account: AccountDetail, tmp_path: Path) -> None:
    save_file_path = tmp_path / "login_save.yaml"

    async with GradescopeConnect(login_save_path=save_file_path).run_test() as pilot:  # type: Pilot
        await pilot.pause()
        assert isinstance(pilot.app.screen, LoginScreen)
        assert pilot.app.screen.login_save_path == save_file_path  # type: ignore

        await enter_account_detail(pilot, gs_account, remember_me=True)

        await pilot.click("#login_btn")
        await pilot.pause()

        assert isinstance(pilot.app.screen, CourseScreen)
        assert save_file_path.exists()

    async with GradescopeConnect(login_save_path=save_file_path).run_test() as pilot:  # type: Pilot
        await pilot.pause()
        await pilot.click("#load_saved_btn")
        await pilot.pause()

        email_field = cast(Input, pilot.app.get_widget_by_id("email_input"))
        assert email_field.value == gs_account.email

    async with GradescopeConnect(login_save_path=save_file_path).run_test() as pilot:  # type: Pilot
        await pilot.pause()
        await pilot.click("#load_saved_and_login_btn")
        await pilot.pause(2)

        assert isinstance(pilot.app.screen, CourseScreen)


@pytest.mark.asyncio
async def test_login_failed_gui(
    gs_dummy_account: AccountDetail, main_app_pilot: Pilot
) -> None:
    await enter_account_detail(main_app_pilot, gs_dummy_account)

    await main_app_pilot.click("#login_btn")

    await main_app_pilot.pause()
    assert isinstance(main_app_pilot.app.screen, LoginScreen)

    info = cast(Label, main_app_pilot.app.get_widget_by_id("login_help_info"))
    info_text: Text = cast(Text, info.renderable)
    for text in info_text._text:
        if "Login Failed" in text:
            break
    else:
        pytest.fail("Login failed message not found")


async def run_test_click_course(gs_cid: str, main_app_pilot: Pilot) -> None:
    assert gs_cid in main_app_pilot.app.account.courses  # type: ignore

    course_display = main_app_pilot.app.get_widget_by_id("course_display")
    course_card_id = make_course_car_name(gs_cid)
    course_card = main_app_pilot.app.get_widget_by_id(course_card_id)
    course_display.scroll_to_widget(course_card)
    await main_app_pilot.pause()

    await main_app_pilot.click(f"#{course_card_id}")
    await main_app_pilot.pause()


@pytest.mark.asyncio
async def test_click_course(
    gs_account: AccountDetail, gs_cid: str, main_app_pilot: Pilot
) -> None:
    await enter_account_detail(main_app_pilot, gs_account)
    await main_app_pilot.click("#login_btn")
    await main_app_pilot.pause()

    await run_test_click_course(gs_cid, main_app_pilot)


async def run_test_click_assignment(
    gs_cid: str, gs_aid: str, main_app_pilot: Pilot
) -> None:
    # assume the course is selected already
    await main_app_pilot.click("#refresh_assignments_btn")
    await main_app_pilot.pause()

    assert gs_aid in main_app_pilot.app.account.courses[gs_cid].assignments  # type: ignore

    assignment_data = cast(
        DataTable, main_app_pilot.app.get_widget_by_id("assignment_table")
    )
    assignment_data.focus()
    index = assignment_data.get_row_index(RowKey(gs_aid))

    assignment_data.move_cursor(row=index)


@pytest.mark.asyncio
async def test_click_assignment(
    gs_account: AccountDetail, gs_cid: str, gs_aid: str, main_app_pilot: Pilot
) -> None:
    await enter_account_detail(main_app_pilot, gs_account)
    await main_app_pilot.click("#login_btn")
    await main_app_pilot.pause()

    await run_test_click_course(gs_cid, main_app_pilot)
    await run_test_click_assignment(gs_cid, gs_aid, main_app_pilot)


async def run_upload_autograder() -> None:
    pass


@pytest.mark.asyncio
async def test_autograder_upload(
    gs_account: AccountDetail,
    gs_cid: str,
    gs_aid: str,
    main_app_pilot: Pilot,
    mocker: MockerFixture,
) -> None:
    await enter_account_detail(main_app_pilot, gs_account)
    await main_app_pilot.click("#login_btn")
    await main_app_pilot.pause()

    session = main_app_pilot.app.account.session  # type: ignore
    assignment = GSAssignmentEssential(cid=gs_cid, aid=gs_aid, session=session)

    autograder_upload = PACKED_AUTOGRADER_FOLDER / "add.zip"

    assert autograder_upload.exists()

    async with AutograderUploadApp(
        assignment=assignment, autograder_path=autograder_upload
    ).run_test() as pilot:  # type: Pilot
        await pilot.pause()

        upload_screen = pilot.app.query_one("AutograderUpload")
        assert isinstance(upload_screen, AutograderUpload)

        success_callback_spy: MagicMock = mocker.spy(
            upload_screen,
            "refresh_upload_info",
        )

        await pilot.click("#upload_btn")
        await pilot.pause()  # wait for refresh

        success_callback_spy.assert_called_once()

        # cancel timer to avoid error in teardown
        upload_screen.upload_info_timer.cancel()
