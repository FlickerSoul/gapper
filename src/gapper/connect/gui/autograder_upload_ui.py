from pathlib import Path
from threading import Timer
from typing import cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Pretty, Select

from gapper.connect.api.assignment import DockerStatusJson, GSAssignment
from gapper.connect.api.utils import OSChoices


class Repeat(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class AutograderUpload(Screen):
    BINDINGS = [("ctrl+b", "go_back", "Go Back")]

    def __init__(
        self, *args, assignment: GSAssignment, autograder_path: Path, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.assignment = assignment
        self.autograder_path = autograder_path
        self.upload_info_timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("Uploading Autograder For"),
            Label(f"Assignment: {self.assignment.name}"),
            Label(
                f"Autograder Path: {self.autograder_path and self.autograder_path.absolute()}"
            ),
        )
        yield ScrollableContainer(id="info_container")
        yield ScrollableContainer(id="error_container")
        yield Container(
            Label("Autograder OS:"),
            Select(
                ((case.name, case) for case in OSChoices),
                value=OSChoices.UbuntuV2204,
                id="os_select",
            ),
        )
        yield Button("Upload", id="upload_btn")
        yield Footer()

    @on(Button.Pressed, "#upload_btn")
    async def uploads(self) -> None:
        select: Select[OSChoices] = cast(
            Select[OSChoices], self.get_widget_by_id("os_select")
        )

        info_container = cast(
            ScrollableContainer, self.get_widget_by_id("info_container")
        )
        error_container = cast(
            ScrollableContainer, self.get_widget_by_id("error_container")
        )

        if select is None:
            await error_container.mount(Label("The autograder OS is unset."))
            return

        try:
            await self.assignment.upload_autograder(self.autograder_path, select.value)
            await info_container.mount(Label("Uploaded autograder successfully."))
        except Exception as e:
            await error_container.mount(
                Label("Cannot upload autograder due to Error."), Label(str(e))
            )
            return
        else:
            self.upload_info_timer = Repeat(1, self.refresh_upload_info)
            self.upload_info_timer.start()

    def action_go_back(self) -> None:
        if self.upload_info_timer:
            self.upload_info_timer.cancel()

    async def refresh_upload_info(self) -> None:
        error_container = cast(
            ScrollableContainer, self.get_widget_by_id("error_container")
        )
        info_container = cast(
            ScrollableContainer, self.get_widget_by_id("info_container")
        )
        docker_status: DockerStatusJson = self.assignment.get_docker_build_status()

        if docker_status["status"] == "built":
            self.upload_info_timer.cancel()

        await info_container.remove_children()
        await error_container.remove_children()

        # TODO: better display of docker status
        await info_container.mount(Pretty(docker_status["stdout"]))
        await error_container.mount(Pretty(docker_status["stderr"]))
