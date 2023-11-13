from textual import on
from textual.app import App
from textual.widget import Widget

from gapper.connect.gui.messages import LoadingEnd, LoadingStart


class LoadingHandler(App):
    @on(LoadingStart)
    async def handle_loading_start(self) -> None:
        self.sub_title = "Loading..."

    @on(LoadingEnd)
    async def handle_loading_end(self) -> None:
        self.sub_title = ""


class LoadingIssuer(Widget):
    def start_loading(self) -> None:
        self.app.post_message(LoadingStart())
        self.log.debug("Starting loading")

    def end_loading(self) -> None:
        self.app.post_message(LoadingEnd())
        self.log.debug("Ending loading")

    def __enter__(self) -> None:
        self.start_loading()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.end_loading()
