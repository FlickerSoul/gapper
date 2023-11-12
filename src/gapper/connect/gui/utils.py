import os
from pathlib import Path

from textual.features import parse_features
from textual.validation import Regex

EMAIL_VALIDATE_REGEX = Regex(r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$")

LOGIN_SAVE_FILE_NAME = "gs_account.yaml"

DEFAULT_LOGIN_SAVE_PATH = Path.home() / ".config/gapper/" / LOGIN_SAVE_FILE_NAME


def add_debug_to_app(flag: bool) -> None:
    """Add debug features to the textual app.

    :seealso https://github.com/Textualize/textual-dev/blob/main/src/textual_dev/cli.py
    """
    if flag:
        features = set(parse_features(os.environ.get("TEXTUAL", "")))
        features.add("debug")
        features.add("devtools")
        os.environ["TEXTUAL_SHOW_RETURN"] = "1"
        os.environ["TEXTUAL"] = ",".join(sorted(features))
