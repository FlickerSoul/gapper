from pathlib import Path

from textual.app import App, ComposeResult

from gapper.connect.api.assignment import GSAssignment, GSAssignmentEssential
from gapper.connect.gui.autograder_upload_ui import AutograderUpload


class AutograderUploadApp(App):
    def __init__(
        self,
        *args,
        assignment: GSAssignment | GSAssignmentEssential,
        autograder_path: Path,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.assignment = assignment
        self.autograder_path = autograder_path

    def compose(self) -> ComposeResult:
        yield AutograderUpload(
            assignment=self.assignment,
            autograder_path=self.autograder_path,
            id="autograder_uploader",
        )
