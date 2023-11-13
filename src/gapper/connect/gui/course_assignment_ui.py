from __future__ import annotations

from typing import cast

from rich.console import Group
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.events import Click
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, Static

from gapper.connect.api.account import GSAccount
from gapper.connect.api.course import GSCourse
from gapper.connect.gui.assignments_ui import AssignmentArea
from gapper.connect.gui.messages import AccountSave

_COURSE_SIDE_BAR_SIZE = 38


class CourseCard(Static):
    class CourseCardSelected(Message):
        def __init__(self, card: CourseCard) -> None:
            super().__init__()
            self.card = card

    def __init__(self, course: GSCourse, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.course = course

    def compose(self) -> ComposeResult:
        yield Label(
            "<" + ("=" * (_COURSE_SIDE_BAR_SIZE - 2)) + ">",
            id=f"selected_{self.course.cid}",
            classes="hidden",
        )

        inner = Group(
            Text(f"{self.course.name}", style=Style(bold=True, italic=True)),
            Text("\n"),
            Text(f"{self.course.assignment_count}"),
        )

        yield Label(
            Panel(
                inner,
                title=self.course.shortname,
                subtitle=f"{self.course.year} {self.course.term} ({self.course.cid})",
                width=_COURSE_SIDE_BAR_SIZE,
            )
        )

    def on_click(self, _: Click) -> None:
        self.post_message(CourseCard.CourseCardSelected(self))

    async def toggle_select(self) -> None:
        select_indicator = self.get_widget_by_id(f"selected_{self.course.cid}")
        if select_indicator.has_class("hidden"):
            select_indicator.remove_class("hidden")
        else:
            select_indicator.add_class("hidden")


def make_course_car_name(cid: str) -> str:
    return f"course_car_{cid}"


class CourseDisplay(Static):
    class CourseRefresh(Message):
        pass

    def __init__(self, account: GSAccount, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.account = account

    def compose(self) -> ComposeResult:
        yield ScrollableContainer(id="course_list")

    async def _load_courses(self) -> None:
        self.log.debug("Loading courses")
        course_list_ui: ScrollableContainer = cast(
            ScrollableContainer, self.get_child_by_id("course_list")
        )

        await course_list_ui.mount(
            *(
                CourseCard(
                    course,
                    classes="course_card",
                    id=make_course_car_name(course.cid),
                )
                for course in sorted(
                    self.account.courses.values(),
                    key=lambda c: (int(c.inactive), c.year, c.term),
                )
            )
        )

        self.log.debug(f"Finished loading {len(self.account.courses)} courses")

    async def on_mount(self) -> None:
        if self.account.courses:
            await self._load_courses()
        else:
            self.post_message(type(self).CourseRefresh())

    async def refresh_course(self) -> None:
        await self.get_child_by_id("course_list").remove_children()
        await self.account.get_admin_courses()
        self.app.post_message(AccountSave())

        await self._load_courses()


class CourseScreen(Screen):
    CSS_PATH = "courses_assignment_ui.tcss"
    BINDINGS = [
        ("ctrl+r", "refresh_course", "Refresh Course List"),
    ]

    def __init__(self, account: GSAccount, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.log.debug(f"Loaded course screen for {account.email}")
        self.log.debug(f"Account has {len(account.courses)} courses")

        self.account = account
        self.selected: CourseCard | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield CourseDisplay(self.account, id="course_display")
        yield AssignmentArea(id="assignment_area")
        yield Footer()

    @on(CourseDisplay.CourseRefresh)
    async def action_refresh_course(self) -> None:
        course_display: CourseDisplay = cast(
            CourseDisplay, self.get_widget_by_id("course_display")
        )

        await course_display.refresh_course()

    @on(CourseCard.CourseCardSelected)
    async def handle_course_select(self, event: CourseCard.CourseCardSelected) -> None:
        if self.selected is not None:
            await self.selected.toggle_select()

        self.selected = event.card
        await self.selected.toggle_select()

        assignment_area: AssignmentArea = cast(
            AssignmentArea, self.get_widget_by_id("assignment_area")
        )
        await assignment_area.load_course(event.card.course)
