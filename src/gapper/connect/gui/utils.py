from pathlib import Path

from textual.validation import Regex

EMAIL_VALIDATE_REGEX = Regex(r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$")

LOGIN_SAVE_FILE_NAME = ".gs_account.save"

DEFAULT_LOGIN_SAVE_PATH = Path.home() / LOGIN_SAVE_FILE_NAME
