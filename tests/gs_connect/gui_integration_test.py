import os
from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from rich.text import Text
from textual.widgets import Input, Label

from gapper.connect.gui.app_ui import GradescopeConnect
from gapper.connect.gui.course_assignment_ui import CourseScreen
from gapper.connect.gui.login_ui import LoginScreen
from tests.gs_connect.conftest import AccountDetail

if TYPE_CHECKING:
    from textual.pilot import Pilot  # noqa: unused-import


@contextmanager
def suppress():
    with open(os.devnull, "w") as null:
        with redirect_stdout(null):
            yield


@pytest.mark.asyncio
async def test_login_gui(gs_account: AccountDetail) -> None:
    app = GradescopeConnect()
    async with app.run_test() as pilot:  # type: Pilot
        with suppress():
            await pilot.pause()

            await pilot.click("#email_input")
            await pilot.press(*gs_account.email)
            await pilot.click("#password_input")
            await pilot.press(*gs_account.password)

            await pilot.click("#login_btn")

            await pilot.pause()

            assert isinstance(pilot.app.screen, CourseScreen)


@pytest.mark.asyncio
async def test_login_save(gs_account: AccountDetail, tmp_path: Path) -> None:
    save_file_path = tmp_path / "login_save.yaml"

    async with GradescopeConnect(
        login_save_path=save_file_path
    ).run_test() as pilot:  # type: Pilot
        with suppress():
            await pilot.pause()
            assert isinstance(pilot.app.screen, LoginScreen)
            assert pilot.app.screen.login_save_path == save_file_path  # type: ignore

            await pilot.click("#email_input")
            await pilot.press(*gs_account.email)
            await pilot.click("#password_input")
            await pilot.press(*gs_account.password)
            await pilot.click("#remember_me")
            await pilot.click("#login_btn")
            await pilot.pause()

            assert isinstance(pilot.app.screen, CourseScreen)
            assert save_file_path.exists()

    async with GradescopeConnect(
        login_save_path=save_file_path
    ).run_test() as pilot:  # type: Pilot
        with suppress():
            await pilot.pause()
            await pilot.click("#load_saved_btn")
            await pilot.pause()

            email_field = cast(Input, pilot.app.get_widget_by_id("email_input"))
            assert email_field.value == gs_account.email

    async with GradescopeConnect(
        login_save_path=save_file_path
    ).run_test() as pilot:  # type: Pilot
        with suppress():
            await pilot.pause()
            await pilot.click("#load_saved_and_login_btn")
            await pilot.pause(2)

            assert isinstance(pilot.app.screen, CourseScreen)


@pytest.mark.asyncio
async def test_login_failed_gui(gs_dummy_account: AccountDetail) -> None:
    app = GradescopeConnect()

    async with app.run_test() as pilot:  # type: Pilot
        with suppress():
            await pilot.pause()

            await pilot.click("#email_input")
            await pilot.press(*gs_dummy_account.email)
            await pilot.click("#password_input")
            await pilot.press(*gs_dummy_account.password)

            await pilot.click("#login_btn")

            await pilot.pause()
            assert isinstance(pilot.app.screen, LoginScreen)

            info = cast(Label, pilot.app.get_widget_by_id("login_help_info"))
            info_text: Text = cast(Text, info.renderable)
            for text in info_text._text:
                if "Login Failed" in text:
                    break
            else:
                pytest.fail("Login failed message not found")
