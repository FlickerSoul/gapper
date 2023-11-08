from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class GradescopeConnect(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
