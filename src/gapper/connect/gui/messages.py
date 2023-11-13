"""Global messages for the GUI."""
from textual.message import Message


class AccountSave(Message):
    def __init__(self, save: bool = False) -> None:
        super().__init__()
        self.save = save


class LoadingStart(Message):
    pass


class LoadingEnd(Message):
    pass
