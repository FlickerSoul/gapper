import traceback

import yaml
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import var
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    Pretty,
    Static,
)

from gapper.connect.api.account import GSAccount
from gapper.connect.gui.utils import DEFAULT_LOGIN_SAVE_PATH


class LoginArea(Static):
    class LoggedIn(Message):
        def __init__(self, account: GSAccount, save: bool) -> None:
            super().__init__()
            self.account = account
            self.save = save

    account = var(None)

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Email", classes="label"),
            Input(placeholder="Gradescope Email", id="email_input"),
            Static("Password", classes="label"),
            Input(
                placeholder="Gradescope Password", password=True, id="password_input"
            ),
            classes="inputs",
        )
        yield Container(
            Checkbox("Save Login Info", id="remember_me", value=False),
            Checkbox("No Verify SSL", id="no_verify", value=False),
            classes="options",
        )
        yield Container(
            Button("Load Login Info", id="load_login_info_btn"),
            Button("Login", id="login_btn"),
            classes="buttons",
        )

        yield Container(
            Label("Please input your email and password to login."),
            Label("Alternatively, you can load your login info from a file."),
            ScrollableContainer(id="login_help_info"),
        )

    @on(Button.Pressed, selector="#load_login_info_btn")
    async def handle_load_login_info(self) -> None:
        info_section = self.get_widget_by_id("login_help_info")
        await info_section.remove_children()

        account_save_path = DEFAULT_LOGIN_SAVE_PATH

        try:
            self.account = GSAccount.from_yaml(account_save_path)
            self.account.spawn_session()
            self.get_widget_by_id("email_input").value = self.account.email
            self.get_widget_by_id("password_input").value = self.account.password
            self.get_widget_by_id("remember_me").value = True
        except FileNotFoundError as e:
            await info_section.mount(
                Label("Cannot load login info because the file does not exist."),
                Pretty(e),
                Pretty(traceback.format_tb(e.__traceback__)),
            )
        except yaml.YAMLError as e:
            await info_section.mount(
                Label("Cannot load login info because the file is invalid."),
                Label("You can try remove old login info my using"),
                Label(f"rm {DEFAULT_LOGIN_SAVE_PATH.absolute()}"),
                Pretty(e),
                Pretty(traceback.format_tb(e.__traceback__)),
            )
        except Exception as e:
            await info_section.mount(
                Label("Cannot load login info because of an unknown error."),
                Label("You can try remove old login info my using"),
                Label(f"rm {DEFAULT_LOGIN_SAVE_PATH.absolute()}"),
                Pretty(e),
                Pretty(traceback.format_tb(e.__traceback__)),
            )

    @on(Button.Pressed, selector="#login_btn")
    async def handle_login(self) -> None:
        info_section = self.get_widget_by_id("login_help_info")
        await info_section.remove_children()

        try:
            await self.get_child_by_id("login_failed").remove()
        except NoMatches:
            pass

        email = self.get_widget_by_id("email_input").value
        password = self.get_widget_by_id("password_input").value
        remember_me = self.get_widget_by_id("remember_me").value
        no_verify = self.get_widget_by_id("no_verify").value

        if self.account is None:
            self.account = GSAccount(email, password).spawn_session()

        if no_verify:
            self.account.no_verify()

        account_save_path = DEFAULT_LOGIN_SAVE_PATH

        try:
            await self.account.login(remember_me)
        except ValueError:
            self.account = None
            await info_section.mount(Label("Login Failed"))
        else:
            if account_save_path:
                self.account.to_yaml(account_save_path)

            self.post_message(self.LoggedIn(self.account, remember_me))


class LoginScreen(Screen):
    CSS_PATH = "login.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield LoginArea(id="login_area")
        yield Footer()
