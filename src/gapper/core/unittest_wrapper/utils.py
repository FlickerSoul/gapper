from __future__ import annotations

from typing import Any, Callable, Protocol

from gapper.core.test_parameter import TestParam
from gapper.core.types import ResultBundle
from gapper.core.utils import CaptureStdout


class ContextManager(dict):
    """A context manager that is also a dict."""

    def __getattr__(self, item: str) -> Any:
        """Get the item from the dict."""
        try:
            return self[item]
        except KeyError as e:
            raise AttributeError from e


class EvalFn[Input, Output](Protocol):
    """The evaluation function type."""

    def __call__(self, to_be_eval: Input, param: TestParam) -> ResultBundle:
        """Evaluate the to_be_eval with test param."""
        ...


def stdout_cm_adder[Output](
    fn: Callable[..., Output]
) -> Callable[..., ResultBundle[Output]]:
    def _wrapper(self, *args, **kwargs) -> Any:
        with CaptureStdout(capture=self.problem.config.check_stdout) as cm:
            res = fn(self, *args, **kwargs)

        return ResultBundle(res, cm.value)

    return _wrapper
