"""Problem configuration."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Optional, TypedDict

from gapper.core.problem.extras.gradescope_connect import GSConnectConfig


class ProblemConfigExtra(TypedDict):
    """Extra problem configuration dictionary."""

    gs_connect: Optional[GSConnectConfig]


@dataclass
class ProblemConfig:
    """Problem configuration.

    :param check_stdout: Whether to check the stdout of the solution.
    :param mock_input: Whether to mock the input of the solution.
    :param captured_context: The context to capture from the submission.
    :param easy_context: Whether to use context directly in gap override tests.
    :param is_script: Whether this problem is a script.
    :param extras: Extra problem configuration dictionary.
    """

    check_stdout: bool = False
    mock_input: bool = False
    captured_context: Iterable[str] = ()
    easy_context: bool = True
    is_script: bool = False
    extras: ProblemConfigExtra = field(default_factory=lambda: defaultdict(None))
