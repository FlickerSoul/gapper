import traceback
from pathlib import Path
from typing import cast

import yaml
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.message import Message
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    Static,
)

from gapper.connect.api.account import GSAccount
from gapper.connect.gui.messages import AccountSave
from gapper.connect.gui.utils import DEFAULT_LOGIN_SAVE_PATH


class LoginScreen(Screen):
    CSS_PATH = "login_ui.tcss"

    class LoggedIn(Message):
        """Message sent when the user has logged in."""

        def __init__(
            self, account: GSAccount, save: bool, login_save_path: Path
        ) -> None:
            super().__init__()
            self.account = account
            self.save = save
            self.login_save_path = login_save_path

    def __init__(
        self,
        *args,
        account: GSAccount | None = None,
        login_save_path: Path | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.account = account
        self.login_save_path: Path = login_save_path or DEFAULT_LOGIN_SAVE_PATH

    def compose(self) -> ComposeResult:
        """Compose the login area."""
        yield Header()
        yield Container(
            Static("Email", classes="label"),
            Input(placeholder="Gradescope Email", id="email_input"),
            Static("Password", classes="label"),
            Input(
                placeholder="Gradescope Password",
                password=True,
                id="password_input",
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
            Label(
                f"The saved login will be loaded from '{self.login_save_path.absolute()}'"
            ),
            ScrollableContainer(Label(id="login_help_info")),
        )
        yield Footer()

    @on(Button.Pressed, selector="#load_saved_and_login_btn")
    async def handle_load_saved_and_login(self) -> None:
        """Handle the load saved and login button."""
        await self.handle_load_saved()
        if self.account is not None:
            await self.handle_login()

    @on(Button.Pressed, selector="#load_saved_btn")
    async def handle_load_saved(self) -> None:
        """Handle the load saved button."""
        info_label = cast(Label, self.get_widget_by_id("login_help_info"))

        try:
            self.account = GSAccount.from_yaml(self.login_save_path).spawn_session()
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
                    "Successfully loaded login info from file.\n",
                    style="bold green",
                )
            case yaml.YAMLError():
                prompt_text.append(
                    "Cannot load login info because the file is invalid.\n",
                    style="bold red",
                )
                prompt_text.append(
                    "You can try remove old login info my using\n"
                    f"rm {self.login_save_path.absolute()}\n",
                    style="red",
                )
            case FileNotFoundError():
                prompt_text.append(
                    "Cannot load login info because the save does not exist.\n",
                    style="bold red",
                )
                prompt_text.append(
                    f"Please check if the file {self.login_save_path.absolute()} exists.\n",
                    style="red",
                )
            case Exception():
                prompt_text.append(
                    "Cannot load login info because of an unknown error.\n",
                    style="bold red",
                )
                prompt_text.append(
                    "You can try remove old login info my using\n"
                    f"rm {self.login_save_path.absolute()}\n",
                    style="red",
                )

        if error is not None:
            prompt_text.append(f"{error}\n")
            prompt_text.append("".join(traceback.format_tb(error.__traceback__)))

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

        use_cookie = bool(self.account.cookies)
        if use_cookie:
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

        try:
            await self.account.login(remember_me)
        except ValueError:
            self.account = None
            prompt = Text("Login Failed! ", style="bold red")
            if use_cookie:
                prompt.append("Your cookies might have expired. ", style="red")
            else:
                prompt.append("Please check your email and password. ", style="red")
            info_label.update(prompt)
        else:
            self.post_message(
                self.LoggedIn(self.account, remember_me, self.login_save_path)
            )
            self.app.post_message(AccountSave())
