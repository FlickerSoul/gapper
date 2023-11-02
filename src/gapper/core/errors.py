"""This module contains the error classes used in the framework."""

import traceback
from textwrap import indent
from types import TracebackType
from typing import Iterable, List


class ErrorFormatter(Exception):
    def extract_user_traceback(self, grader_path: str | None = None) -> List[str]:
        """Extract the user traceback from the exception.

        :param grader_path: The path to the grader file.
        """
        tbs: List[traceback.FrameSummary] = traceback.extract_tb(self.__traceback__)
        if grader_path is None:
            filtered_tbs = filter(lambda tb: "gapper" not in tb.filename, tbs)
        else:
            filtered_tbs = filter(lambda tb: grader_path not in tb.filename, tbs)
        return traceback.format_list(list(filtered_tbs))

    def extract_user_traceback_str(self, grader_path: str | None = None) -> str:
        """Extract the user traceback from the exception as a string."""
        return "\n".join(self.extract_user_traceback(grader_path))

    def extract_traceback_str(self) -> str:
        """Extract the traceback from the exception as a string."""
        return "\n".join(traceback.format_tb(self.__traceback__))

    def _get_last_tb(self, tb: TracebackType) -> TracebackType:
        while tb.tb_next is not None:
            tb = tb.tb_next
        return tb

    def format_args(self, indent_num: int = 0) -> str:
        """Format the arguments of the error message.

        :param indent_num: The number of spaces to indent the message.
        """
        return indent(
            ",\n".join(str(arg).rstrip("\n") for arg in self.args), " " * indent_num
        )

    def format(self) -> str:
        """Format the error message."""
        raise NotImplementedError


class TestFailedError(ErrorFormatter):
    """Raised when a test fails."""

    def format(self) -> str:
        return f"Test Assertion Failed. The reason is following: \n{self.format_args(indent_num=2)}\n"


class SubmissionSyntaxError(ErrorFormatter):
    """Raised when a submission has syntax errors."""

    def format(self) -> str:
        return f"The submission has syntax errors. The reason is following: \n{self.format_args(indent_num=2)}\n"


class InternalError(ErrorFormatter):
    """Raised when an internal error occurs in the framework."""

    def format(self) -> str:
        tb_info = indent(
            tb_str if (tb_str := self.extract_traceback_str()) else "Not Provided\n",
            "  ",
        )
        return (
            f"Internal Error. "
            f"The reason is following: \n{self.format_args(indent_num=2)}\n"
            f"Stack Trace: \n{tb_info}"
        )


class NoSubmissionError(ErrorFormatter):
    """Raised when no submission is loaded."""

    def format(self) -> str:
        return "No submission {} is found."


class MultipleSubmissionError(ErrorFormatter):
    def format(self) -> str:
        return "Multiple submissions are found."


class MissingContextValueError(ErrorFormatter):
    def __init__(self, value_name: str):
        super().__init__()
        self.value_name = value_name

    def format(self) -> str:
        return f"Cannot find variable {self.value_name} in the context."


class MultipleContextValueError(ErrorFormatter):
    def __init__(self, value_name: str):
        super().__init__()
        self.value_name = value_name

    def format(self) -> str:
        return f"Multiple values for variable {self.value_name} in the context."


class NoProblemDefinedError(ErrorFormatter):
    def format(self) -> str:
        return "No problem is defined."


class MultipleProblemsDefinedError(ErrorFormatter):
    def __init__(self, names: Iterable[str]):
        super().__init__()
        self.names = names

    @property
    def formatted_names(self) -> str:
        return ", ".join(self.names)

    def format(self) -> str:
        return f"Multiple problems ({self.formatted_names}) are defined."
