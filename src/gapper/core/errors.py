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

    def extract_user_traceback_str(
        self, grader_path: str | None = None, indent_num: int = 0
    ) -> str:
        """Extract the user traceback from the exception as a string."""
        return indent(
            "\n".join(self.extract_user_traceback(grader_path)),
            " " * indent_num,
        )

    def extract_traceback_str(self, indent_num: int = 0) -> str:
        """Extract the traceback from the exception as a string."""
        return indent(
            "\n".join(traceback.format_tb(self.__traceback__)), " " * indent_num
        )

    def _get_last_tb(self, tb: TracebackType) -> TracebackType:
        while tb.tb_next is not None:
            tb = tb.tb_next
        return tb

    def format_args(self, indent_num: int = 0) -> str:
        """Format the arguments of the error message.

        :param indent_num: The number of spaces to indent the message.
        """
        return indent(
            ",\n".join(str(arg).rstrip("\n") for arg in self.args),
            " " * indent_num,
        )

    def format(self) -> str:
        """Format the error message."""
        raise NotImplementedError


class StudentError(ErrorFormatter):
    pass


class TestFailedError(ErrorFormatter):
    """Raised when a test fails."""

    def format(self) -> str:
        return f"Test Assertion Failed. The reason is following: \n{self.format_args(indent_num=2)}\n"


class SubmissionSyntaxError(StudentError):
    """Raised when a submission has syntax errors."""

    def format(self) -> str:
        return (
            f"The submission has syntax errors. "
            f"The reason is following: \n"
            f"{self.format_args(indent_num=2)}\n"
            f"{self.extract_user_traceback_str()}"
        )


class InternalError(ErrorFormatter):
    """Raised when an internal error occurs in the framework."""

    def format(self) -> str:
        tb_info = indent(
            tb_str if (tb_str := self.extract_traceback_str()) else "Not Provided\n",
            "  ",
        )
        return (
            f"Internal Error. Please report this to the developers. \n"
            f"The reason is following: \n{self.format_args(indent_num=2)}\n"
            f"Stack Trace: \n{tb_info}"
        )


class NoSubmissionError(StudentError):
    """Raised when no submission is loaded."""

    def __init__(self, expected_name: str):
        super().__init__(expected_name)

    @property
    def expected_name(self) -> str:
        return self.args[0]

    def format(self) -> str:
        return (
            f"No submission is found.\n"
            f"If you're submitting a script, please name your submission file as '{self.expected_name}'.\n"
            f"If you're writing a function or a class, "
            f"please name your submission fn/class as '{self.expected_name}'.\n"
            f"(without quotes)\n"
        )


class MultipleSubmissionError(StudentError):
    def __init__(self, expected_name: str):
        super().__init__(expected_name)

    @property
    def expected_name(self) -> str:
        return self.args[0]

    def format(self) -> str:
        return (
            f"Multiple submissions are found.\n"
            f"If you're submitting a script, only one submission should named as '{self.expected_name}'.\n"
            f"If you're writing a function or a class, please only name one fn/class as '{self.expected_name}'.\n"
            f"(without quotes)\n"
        )


class MissingContextValueError(StudentError):
    def __init__(self, value_name: str):
        super().__init__(value_name)

    @property
    def value_name(self) -> str:
        return self.args[0]

    def format(self) -> str:
        return (
            f"Cannot find variable '{self.value_name}' in the submission context.\n"
            f"Please check if you have defined it in your submission.\n"
        )


class MultipleContextValueError(StudentError):
    def __init__(self, value_name: str):
        super().__init__(value_name)

    @property
    def value_name(self) -> str:
        return self.args[0]

    def format(self) -> str:
        return (
            f"Multiple values for variable '{self.value_name}' in the context.\n"
            f"Please check if you have defined it multiple times in your submission.\n"
        )


class NoProblemDefinedError(InternalError):
    def format(self) -> str:
        return "No problem is defined."


class MultipleProblemsDefinedError(InternalError):
    def __init__(self, names: Iterable[str]):
        super().__init__(*names)

    @property
    def names(self) -> Iterable[str]:
        return self.args

    @property
    def formatted_names(self) -> str:
        return ", ".join(self.args)

    def format(self) -> str:
        return f"Multiple problems ({self.formatted_names}) are defined."
