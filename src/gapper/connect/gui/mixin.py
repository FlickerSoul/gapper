from textual import on
from textual.app import App

from gapper.connect.gui.messages import LoadingEnd, LoadingStart


class LoadingHandler(App):
    @on(LoadingStart)
    async def handle_loading_start(self) -> None:
        self.sub_title = "Loading..."

    @on(LoadingEnd)
    async def handle_loading_end(self) -> None:
        self.sub_title = ""
