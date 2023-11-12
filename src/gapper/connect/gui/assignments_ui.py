from typing import cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Button, DataTable, Label, Static

from gapper.connect.api.course import GSCourse
from gapper.connect.gui.messages import AccountSave

_COLUMNS = [
    "Name",
    "Points",
    "Due",
    "Late Due",
    "Released",
    "Submissions",
    "Percent Graded",
]


class AssignmentArea(Static):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.course: GSCourse | None = None

    async def load_course(self, course: GSCourse) -> None:
        self.log.debug(f"Loaded course {course.name}")
        self.course = course
        await self.load_assignments()

    async def load_assignments(self) -> None:
        assignment_table: DataTable = cast(
            DataTable, self.get_widget_by_id("assignment_table")
        )

        assignment_table.clear()
        self.log.debug(f"Cleared assignment table")

        if self.course is None:
            self.log.debug("No course loaded, cannot load assignments")
            return

        self.log.debug("Loading assignments")

        for key, assignment in self.course.assignments.items():
            assignment_table.add_row(
                assignment.name,
                assignment.points,
                assignment.due_date,
                assignment.hard_due_date,
                assignment.release_date,
                assignment.submissions,
                f"{assignment.percent_graded}%",
                key=key,
            )

    def compose(self) -> ComposeResult:
        yield Container(
            Button("Refresh Assignments", id="refresh_assignments_btn"),
            Button("Upload Autograder", id="upload_autograder_btn"),
            Button("Add Assignment", id="add_assignment_btn"),
            id="assignment_buttons",
        )
        yield ScrollableContainer(id="info_container")
        yield DataTable(id="assignment_table")

    async def on_mount(self) -> None:
        assignment_table: DataTable = cast(
            DataTable, self.get_widget_by_id("assignment_table")
        )

        self.log.debug(f"Mounting assignment table {assignment_table}")
        for col in _COLUMNS:
            assignment_table.add_column(col, key=col)

        await self.load_assignments()

    @on(Button.Pressed, selector="#refresh_assignments_btn")
    async def handle_assignment_refresh(self) -> None:
        info_container: ScrollableContainer = cast(
            ScrollableContainer, self.get_widget_by_id("info_container")
        )
        await info_container.remove_children()
        if self.course is None:
            self.log.debug("No course loaded, cannot refresh assignments")
            await info_container.mount(
                Label("No course loaded, cannot refresh assignments")
            )
            return

        self.log.debug("Refreshing assignments")

        await self.course.get_assignments()
        self.log.debug(f"Got {len(self.course.assignments)} assignments")

        self.post_message(AccountSave())
        await self.load_assignments()

    @on(Button.Pressed, selector="#add_assignment_btn")
    async def handle_assignment_create(self) -> None:
        pass

    @on(Button.Pressed, selector="#upload_autograder_btn")
    async def handle_assignment_upload(self) -> None:
        pass
