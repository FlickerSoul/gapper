from typing import cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.message import Message
from textual.widgets import Button, DataTable, Label, Static

from gapper.connect.api.assignment import GSAssignment
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
    class AutograderUpload(Message):
        def __init__(self, assignment: GSAssignment) -> None:
            super().__init__()
            self.assignment = assignment

    class CreateNewAssignment(Message):
        def __init__(self, course: GSCourse) -> None:
            super().__init__()
            self.course = course

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.course: GSCourse | None = None
        self.selected_assignment: GSAssignment | None = None

    def compose(self) -> ComposeResult:
        yield Container(
            Button("Refresh Assignments", id="refresh_assignments_btn"),
            Button("Upload Autograder", id="upload_autograder_btn"),
            Button("Add Assignment", id="add_assignment_btn"),
            id="assignment_buttons",
        )
        yield Container(id="course_loaded_container")
        yield ScrollableContainer(id="info_container")
        yield DataTable(id="assignment_table")

    async def on_mount(self) -> None:
        assignment_table: DataTable = cast(
            DataTable, self.get_widget_by_id("assignment_table")
        )

        await self.change_course_name()

        self.log.debug(f"Mounting assignment table {assignment_table}")
        for col in _COLUMNS:
            assignment_table.add_column(col, key=col)

        await self.load_assignments()

    async def load_course(self, course: GSCourse) -> None:
        self.log.debug(f"Loaded course {course and course.name}")
        self.course = course
        await self.clear_info_section()
        await self.change_course_name()

        if not self.course.assignments:
            self.log.debug("No assignments, refreshing")
            await self.refresh_assignment()

        await self.load_assignments()

    async def clear_info_section(self) -> ScrollableContainer:
        info_container: ScrollableContainer = cast(
            ScrollableContainer, self.get_widget_by_id("info_container")
        )
        await info_container.remove_children()

        return info_container

    async def change_course_name(self) -> None:
        container = cast(Container, self.get_widget_by_id("course_loaded_container"))
        await container.remove_children()
        if self.course:
            await container.mount(Label(f"Loaded Course: {self.course.name}"))
        else:
            await container.mount(
                Label("No course loaded. Please select from the left.")
            )

    async def load_assignments(self) -> None:
        assignment_table: DataTable = cast(
            DataTable, self.get_widget_by_id("assignment_table")
        )

        assignment_table.clear()
        self.log.debug("Cleared assignment table")

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

        info_section = await self.clear_info_section()
        await info_section.mount(Label("Loaded assignments"))

    @on(Button.Pressed, selector="#refresh_assignments_btn")
    async def handle_assignment_refresh(self) -> None:
        await self.refresh_assignment()
        await self.load_assignments()

    @on(DataTable.CellSelected, selector="#assignment_table")
    async def handle_assignment_cell_selected(
        self, message: DataTable.CellSelected
    ) -> None:
        self.log.debug(f"Selected assignment {message.cell_key.row_key.value}")
        await self._load_selected(message.cell_key.row_key.value)

    @on(DataTable.RowSelected, selector="#assignment_table")
    async def handle_assignment_row_selected(
        self, message: DataTable.RowSelected
    ) -> None:
        self.log.debug(f"Selected assignment {message.row_key.value}")
        await self._load_selected(message.row_key.value)

    async def _load_selected(self, key: str | None) -> None:
        self.selected_assignment = self.course.assignments.get(key, None)
        info_container: ScrollableContainer = await self.clear_info_section()
        await info_container.mount(
            Label(
                f"Selected assignment {self.selected_assignment and self.selected_assignment.name}"
            )
        )

    async def refresh_assignment(self) -> None:
        info_container: ScrollableContainer = await self.clear_info_section()
        await info_container.mount(Label("Loading assignments..."))

        if self.course is None:
            self.log.debug("No course loaded, cannot refresh assignments")
            await info_container.mount(
                Label("No course loaded, cannot refresh assignments")
            )
            return

        self.log.debug("Refreshing assignments")
        await self.course.get_assignments()
        self.log.debug(f"Got {len(self.course.assignments)} assignments")

        self.app.post_message(AccountSave())

    @on(Button.Pressed, selector="#add_assignment_btn")
    async def handle_assignment_create(self) -> None:
        if self.course is None:
            await self.get_widget_by_id("info_container").mount(
                Label("No course selected")
            )
            return

        self.post_message(type(self).CreateNewAssignment(self.course))

    @on(Button.Pressed, selector="#upload_autograder_btn")
    async def handle_assignment_upload(self) -> None:
        if self.selected_assignment is None:
            await self.get_widget_by_id("info_container").mount(
                Label("No assignment selected")
            )
            return
        self.post_message(type(self).AutograderUpload(self.selected_assignment))
