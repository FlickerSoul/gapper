"""The module for the test result."""
from __future__ import annotations

from dataclasses import dataclass, field
from textwrap import indent
from typing import TYPE_CHECKING, Iterable, List

if TYPE_CHECKING:
    from gapper.core.errors import ErrorFormatter
    from gapper.gradescope.datatypes.gradescope_output import PassStateType


@dataclass
class TestResult:
    """Test result for a single test case.

    :param default_name: The default name of the test.
    :param name: The name of the test.
    :param score: The score obtained by the test.
    :param max_score: The max score can obtained for the test.
    :param weight: The weight of the test.
    :param extra_points: The extra points of the test, applied when the test is passed.
    :param errors: The errors of the test.
    :param pass_status: The pass status of the test.
    :param hidden: Whether the test is hidden.
    :param descriptions: The descriptions of the test.
    """

    default_name: str
    name: str | None = None
    score: float | None = field(default=None)
    max_score: float | None = field(default=None)
    weight: int | None = field(default=None)
    extra_points: float | None = field(default=None)
    errors: List[ErrorFormatter] = field(default_factory=list)
    pass_status: PassStateType | None = field(default=None)
    hidden: bool = False
    descriptions: List[str] = field(default_factory=list)

    @property
    def rich_test_name(self) -> str:
        """The name of the test, with the default name prepended if the name is unset."""
        name = f"{self.name} " if self.name else ""
        default_name = self.default_name
        return "{}{}".format(name, default_name)

    @property
    def rich_test_output(self) -> str:
        """The description output of the test, with the score and max score appended if set."""
        pass_status_msg = self.pass_status.capitalize() if self.pass_status else ""

        description_info = indent("\n".join(self.descriptions), " " * 2)
        description_msg = (
            "Description(s): \n" + description_info if self.descriptions else ""
        )

        error_info = indent(
            "\n".join(err.format() for err in self.errors),
            " " * 2,
        )
        error_msg = "Error(s): \n" + error_info if self.errors else ""

        messages = list(filter(bool, [pass_status_msg, description_msg, error_msg]))
        if len(messages) == 0:
            return "<No Description>"
        else:
            return "\n".join(messages)

    def set_name(self, name: str) -> None:
        """Set the name of the test.

        This does not modify the default name.
        """
        self.name = name

    def add_description(self, *detail: str) -> None:
        """Add a description to the test.

        New descriptions are added as newlines to the end of the existing descriptions.

        :param detail: The description to add.
        """
        self.descriptions.extend(detail)

    def set_descriptions(self, detail: Iterable[str]) -> None:
        """Set the description of the test.

        This overrides all the existing descriptions.

        :param detail: The description to set.
        """
        self.descriptions = list(detail)

    def set_hidden(self, hidden: bool) -> None:
        """Set the hidden status of the test.

        :param hidden: Whether the test is hidden.
        """
        self.hidden = hidden

    def set_score(self, score: float) -> None:
        """Set the score of the test.

        :param score: The score to set.
        """
        self.score = score

    def set_max_score(self, max_score: float | None) -> None:
        """Set the max score of the test.

        :param max_score: The max score of this test case to set.
        """
        self.max_score = max_score

    def set_weight(self, weight: int | None) -> None:
        """Set the weight of the test.

        :param weight: The weight of this test case to set.
        """
        self.weight = weight

    def set_extra_points(self, score: float | None) -> None:
        """Set the extra points of the test.

        :param score: The extra points of this test case to set.
        """
        self.extra_points = score

    def add_error(self, error: ErrorFormatter, set_failed: bool = True) -> None:
        """Add an error to the test.

        :param error: The error to add.
        :param set_failed: Whether to set the pass status to failed.
        """
        self.errors.append(error)
        if set_failed:
            self.set_pass_status("failed")

    @property
    def is_passed(self) -> bool:
        """Whether the test passed."""
        return self.pass_status == "passed"

    @property
    def is_pass_status_unset(self) -> bool:
        """Whether the pass status is unset."""
        return self.pass_status is None

    def set_pass_status(self, status: PassStateType) -> None:
        """Set the pass status of the test.

        :param status: The pass status to set.
        """
        self.pass_status = status

    def set_default_weight(self) -> None:
        """Set the weight of the test to 1."""
        self.weight = 1
