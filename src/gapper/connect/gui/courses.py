from __future__ import annotations

from typing import List

from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.css.query import NoMatches
from textual.events import Click
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, LoadingIndicator, Static

from gapper.connect.api.account import GSAccount
from gapper.connect.api.course import GSCourse


class CourseCardBackground(Static):
    pass


class CourseCard(Static):
    class CourseCardSelected(Message):
        def __init__(self, card: CourseCard) -> None:
            super().__init__()
            self.card = card

    def __init__(self, course: GSCourse, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.course = course

    def compose(self) -> ComposeResult:
        max_len = max(
            len(self.course.shortname),
            len(self.course.name),
            len(self.course.cid),
            len(self.course.assignment_count),
            len(self.course.term),
        )

        yield Label("=" * max_len, id=f"selected_{self.course.cid}", classes="hidden")
        yield Label("-" * max_len)
        yield Label(self.course.shortname, id="course_shortname")
        yield Label(self.course.name, id="course_name")
        yield Label(self.course.cid, id="course_cid")
        yield Label(self.course.assignment_count, id="course_assignment_count")
        yield Label(self.course.term, id="course_term")
        yield Label("-" * max_len)
        yield CourseCardBackground()

    def on_click(self, _: Click) -> None:
        self.post_message(CourseCard.CourseCardSelected(self))

    def toggle_select(self) -> None:
        select_indicator = self.get_widget_by_id(f"selected_{self.course.cid}")
        if select_indicator.has_class("hidden"):
            select_indicator.remove_class("hidden")
        else:
            select_indicator.add_class("hidden")


class CourseRefresh(Message):
    pass


class CourseDisplay(Static):
    course_list = reactive([], layout=True)

    def __init__(self, account: GSAccount) -> None:
        super().__init__()
        self.account = account
        self.selected: CourseCard | None = None

    def compose(self) -> ComposeResult:
        yield ScrollableContainer(
            LoadingIndicator(id="course_loading", classes="hidden"),
            id="course_list",
        )

    @on(CourseRefresh)
    async def refresh_course(self) -> None:
        await self.get_child_by_id("course_list").remove_children()
        await self.account.get_admin_courses()

        await self._load_courses([*self.account.courses.values()])

    async def _load_courses(self, course_list: List[GSCourse]) -> None:
        self.course_list = course_list
        course_list_ui: ScrollableContainer = self.get_child_by_id("course_list")

        for course in course_list:
            await course_list_ui.mount(CourseCard(course, classes="course_card"))

        try:
            if self.get_widget_by_id("course_loading").has_class("hidden"):
                self.get_widget_by_id("course_loading").add_class("hidden")
        except NoMatches:
            self.log.debug("No loading indicator found, prob when mounting")

    async def on_mount(self) -> None:
        if self.account.courses:
            await self._load_courses([*self.account.courses.values()])
        else:
            self.post_message(CourseRefresh())

    @on(CourseCard.CourseCardSelected)
    def handle_course_select(self, event: CourseCard.CourseCardSelected) -> None:
        if self.selected is not None:
            self.selected.toggle_select()

        self.selected = event.card
        self.selected.toggle_select()


class CourseScreen(Screen):
    CSS_PATH = "courses.tcss"

    def __init__(self, account: GSAccount, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.account = account

    def compose(self) -> ComposeResult:
        yield Header()
        yield CourseDisplay(self.account)
        yield Footer()
