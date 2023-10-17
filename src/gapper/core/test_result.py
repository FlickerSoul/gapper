from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Iterable


if TYPE_CHECKING:
    from gapper.core.errors import ErrorFormatter
    from gapper.gradescope.datatypes.gradescope_output import PassStateType


@dataclass
class TestResult:
    default_name: str
    name: str | None = None
    score: float | None = field(default=None)
    max_score: float | None = field(default=None)
    weight: int | None = field(default=None)
    extra_score: float | None = field(default=None)
    errors: List[ErrorFormatter] = field(default_factory=list)
    pass_status: PassStateType | None = field(default=None)
    hidden: bool = False
    descriptions: List[str] = field(default_factory=list)

    def has_valid_score(self) -> None:
        assert (
            self.score is None or self.score >= 0
        ), f"Score must be non-negative ({self.rich_test_name})."
        assert (
            self.max_score is None or self.max_score >= 0
        ), f"Max score must be non-negative ({self.rich_test_name})."
        assert (
            self.weight is None or self.weight >= 0
        ), f"Weight must be non-negative ({self.rich_test_name}."
        assert (
            self.extra_score is None or self.extra_score >= 0
        ), f"Extra score must be non-negative ({self.rich_test_name})."

    @property
    def rich_test_name(self) -> str:
        name = f"{self.name} " if self.name else ""
        default_name = self.default_name
        return "{}{}".format(name, default_name)

    @property
    def rich_test_output(self) -> str:
        pass_status_msg = self.pass_status.capitalize() if self.pass_status else ""
        descriptions = (
            "Description(s): " + "\n".join(self.descriptions)
            if self.descriptions
            else ""
        )
        error_msg = (
            "Error(s): \n"
            + ("\n".join(err.format() for err in self.errors) if self.errors else "")
            if self.errors
            else ""
        )

        messages = list(filter(bool, [pass_status_msg, descriptions, error_msg]))
        if len(messages) == 0:
            return "<No Description>"
        else:
            return "\n".join(messages)

    def set_name(self, name: str) -> None:
        self.name = name

    def add_description(self, detail: str) -> None:
        self.descriptions.append(detail)

    def set_descriptions(self, detail: Iterable[str]) -> None:
        self.descriptions = list(detail)

    def set_hidden(self, hidden: bool) -> None:
        self.hidden = hidden

    def set_score(self, score: float) -> None:
        self.score = score

    def set_max_score(self, max_score: float | None) -> None:
        self.max_score = max_score

    def set_weight(self, weight: int | None) -> None:
        self.weight = weight

    def set_extra_score(self, score: float | None) -> None:
        self.extra_score = score

    def add_error(self, error: ErrorFormatter, set_failed: bool = True) -> None:
        self.errors.append(error)
        if set_failed:
            self.set_pass_status("failed")

    @property
    def is_passed(self) -> bool:
        return self.pass_status == "passed"

    @property
    def is_pass_status_unset(self) -> bool:
        return self.pass_status is None

    def set_pass_status(self, status: PassStateType) -> None:
        self.pass_status = status
