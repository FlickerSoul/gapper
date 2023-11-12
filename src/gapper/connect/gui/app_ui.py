from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from gapper.connect.api.account import GSAccount
from gapper.connect.gui.assignments_ui import AssignmentArea
from gapper.connect.gui.autograder_upload_ui import AutograderUpload
from gapper.connect.gui.course_assignment_ui import CourseScreen
from gapper.connect.gui.login_ui import LoginArea, LoginScreen
from gapper.connect.gui.messages import AccountSave
from gapper.connect.gui.utils import DEFAULT_LOGIN_SAVE_PATH


class GradescopeConnect(App):
    BINDINGS = [
        ("ctrl+d", "toggle_dark", "Toggle dark mode"),
        ("ctrl+q", "app.quit", "Quit"),
    ]
    SCREENS = {
        "login_screen": LoginScreen(id="login_screen", name="login_screen"),
    }
    debug = True

    def __init__(self, *args, autograder_path: Path | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.account: GSAccount | None = None
        self.save: bool = False
        self.autograder_path = autograder_path

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.push_screen("login_screen")

    @on(LoginArea.LoggedIn)
    async def handle_login(self, message: LoginArea.LoggedIn) -> None:
        self.account = message.account
        self.save = message.save
        self.log.debug(f"Logged in as {self.account.email}")
        await self.push_screen(CourseScreen(account=self.account, name="course_screen"))

    @on(AccountSave)
    async def handle_save(self, message: AccountSave) -> None:
        if self.save or message.save:
            try:
                self.account.to_yaml(DEFAULT_LOGIN_SAVE_PATH)
            except Exception as e:
                self.log.debug(f"Failed to save account: {e}")
        else:
            self.log.debug("Not saving account")

    @on(AssignmentArea.CreateNewAssignment)
    async def handle_create_new_assignment(self) -> None:
        pass

    @on(AssignmentArea.AutograderUpload)
    async def handle_upload_autograder(
        self, event: AssignmentArea.AutograderUpload
    ) -> None:
        await self.push_screen(
            AutograderUpload(
                assignment=event.assignment, autograder_path=self.autograder_path
            )
        )
