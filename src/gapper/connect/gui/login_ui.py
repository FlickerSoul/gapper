import traceback
from typing import cast

import yaml
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.message import Message
from textual.reactive import var
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, Static

from gapper.connect.api.account import GSAccount
from gapper.connect.gui.utils import DEFAULT_LOGIN_SAVE_PATH


class LoginArea(Static):
    class LoggedIn(Message):
        """Message sent when the user has logged in."""

        def __init__(self, account: GSAccount, save: bool) -> None:
            super().__init__()
            self.account = account
            self.save = save

    account = var(None)

    def compose(self) -> ComposeResult:
        """Compose the login area."""
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
            Button("Load Saved and Login", id="load_saved_and_login_btn"),
            Button("Load Saved", id="load_saved_btn"),
            Button("Login", id="login_btn"),
            classes="buttons",
        )

        yield Container(
            Label("Please input your email and password to login."),
            Label("Alternatively, you can load your login info from a file."),
            ScrollableContainer(Label(id="login_help_info")),
        )

    @on(Button.Pressed, selector="#load_saved_and_login_btn")
    async def handle_load_saved_and_login(self) -> None:
        """Handle the load saved and login button."""
        await self.handle_load_saved()
        await self.handle_login()

    @on(Button.Pressed, selector="#load_saved_btn")
    async def handle_load_saved(self) -> None:
        """Handle the load saved button."""
        info_label = cast(Label, self.get_widget_by_id("login_help_info"))

        account_save_path = DEFAULT_LOGIN_SAVE_PATH

        try:
            self.account = GSAccount.from_yaml(account_save_path).spawn_session()
            self.get_widget_by_id("email_input").value = self.account.email
            self.get_widget_by_id("password_input").value = self.account.password
            self.get_widget_by_id("remember_me").value = True
        except Exception as e:
            error = e
        else:
            error = None

        prompt_text = Text()

        match error:
            case None:
                prompt_text.append(
                    "Successfully loaded login info from file.\n", style="bold green"
                )
            case yaml.YAMLError():
                prompt_text.append(
                    "Cannot load login info because the file is invalid.\n",
                    style="bold red",
                )
                prompt_text.append(
                    "You can try remove old login info my using\n"
                    f"rm {DEFAULT_LOGIN_SAVE_PATH.absolute()}\n",
                    style="red",
                )
            case FileNotFoundError():
                prompt_text.append(
                    "Cannot load login info because the save does not exist.\n",
                    style="bold red",
                )
                prompt_text.append(
                    f"Please check if the file {DEFAULT_LOGIN_SAVE_PATH.absolute()} exists.\n",
                    style="red",
                )
            case Exception():
                prompt_text.append(
                    "Cannot load login info because of an unknown error.\n",
                    style="bold red",
                )
                prompt_text.append(
                    "You can try remove old login info my using\n"
                    f"rm {DEFAULT_LOGIN_SAVE_PATH.absolute()}\n",
                    style="red",
                )

        if error is not None:
            prompt_text.append(f"{error}\n")
            prompt_text.append("\n".join(traceback.format_tb(error.__traceback__)))

        info_label.update(prompt_text)

    @on(Button.Pressed, selector="#login_btn")
    async def handle_login(self) -> None:
        """Handle the login button."""
        info_label = cast(Label, self.get_widget_by_id("login_help_info"))

        email = cast(Input, self.get_widget_by_id("email_input")).value
        password = cast(Input, self.get_widget_by_id("password_input")).value
        remember_me = cast(Checkbox, self.get_widget_by_id("remember_me")).value
        no_verify = cast(Checkbox, self.get_widget_by_id("no_verify")).value

        if self.account is None:
            self.account = GSAccount(email, password).spawn_session()

        if self.account.cookies:
            info_label.update(Text("Trying to use cookies to login..."))
        else:
            if email.strip() == "":
                info_label.update(Text("Email cannot be empty!", style="bold red"))
                return

            if password.strip() == "":
                info_label.update(Text("Password is empty!", style="bold red"))
                return

        if no_verify:
            self.account.no_verify()

        account_save_path = DEFAULT_LOGIN_SAVE_PATH

        try:
            await self.account.login(remember_me)
        except ValueError:
            self.account = None
            info_label.update(Text("Login Failed!", style="bold red"))
        else:
            if account_save_path:
                self.account.to_yaml(account_save_path)

            self.post_message(self.LoggedIn(self.account, remember_me))


class LoginScreen(Screen):
    CSS_PATH = "login_ui.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield LoginArea(id="login_area")
        yield Footer()
