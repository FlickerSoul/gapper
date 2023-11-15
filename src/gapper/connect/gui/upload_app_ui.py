from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static

from gapper.connect.api.assignment import GSAssignment, GSAssignmentEssential
from gapper.connect.gui.autograder_upload_ui import AutograderUploadScreen


class AutograderUploadApp(App):
    BINDINGS = [
        ("ctrl+q", "app.quit", "Quit"),
    ]

    CSS = """
        Screen {
            align: center middle;
        }
        
        .quit_prompt {
            width: auto;
        }
    """

    def __init__(
        self,
        *args,
        assignment: GSAssignment | GSAssignmentEssential,
        autograder_path: Path,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.assignment = assignment
        self.autograder_path = autograder_path

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "You can quit this uploader now (ctrl+q) :)", classes="quit_prompt"
        )
        yield Footer()

    async def on_mount(self) -> None:
        await self.push_screen(
            AutograderUploadScreen(
                assignment=self.assignment,
                autograder_path=self.autograder_path,
                id="autograder_uploader",
            )
        )
