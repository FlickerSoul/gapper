from pathlib import Path

from textual.validation import Regex

EMAIL_VALIDATE_REGEX = Regex(r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$")

LOGIN_SAVE_FILE_NAME = "gs_account.yaml"

DEFAULT_LOGIN_SAVE_PATH = Path.home() / ".config/gapper/" / LOGIN_SAVE_FILE_NAME
