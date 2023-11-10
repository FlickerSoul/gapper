from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from gapper.connect.api.account import GSAccount
from gapper.connect.gui.courses import CourseRefresh, CourseScreen
from gapper.connect.gui.login import LoginArea, LoginScreen
from gapper.connect.gui.messages import AccountSave
from gapper.connect.gui.utils import DEFAULT_LOGIN_SAVE_PATH


class GradescopeConnect(App):
    BINDINGS = [
        ("ctrl+d", "toggle_dark", "Toggle dark mode"),
        ("ctrl+r", "refresh_course", "Refresh Course List"),
        ("ctrl+q", "app.quit", "Quit"),
    ]
    SCREENS = {
        "login_screen": LoginScreen(id="login_screen", name="login_screen"),
    }
    debug = True

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.account: GSAccount | None = None
        self.save: bool = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_refresh_course(self) -> None:
        self.post_message(CourseRefresh())

    def on_mount(self) -> None:
        self.push_screen("login_screen")

    @on(LoginArea.LoggedIn)
    def handle_login(self, message: LoginArea.LoggedIn) -> None:
        self.account = message.account
        self.save = message.save
        self.log.debug(f"Logged in as {self.account.email}")
        self.push_screen(CourseScreen(account=self.account, name="course_screen"))

    @on(AccountSave)
    def handle_save(self, message: AccountSave) -> None:
        if self.save or message.save:
            try:
                self.account.to_yaml(DEFAULT_LOGIN_SAVE_PATH)
            except Exception as e:
                self.log.debug(f"Failed to save account: {e}")
        else:
            self.log.debug("Not saving account")
