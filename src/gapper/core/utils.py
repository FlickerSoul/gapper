from __future__ import annotations

import importlib.util
from contextlib import redirect_stdout
from importlib.machinery import ModuleSpec
from io import StringIO
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterable, Protocol, Self, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from gapper.core.unittest_wrapper import TestCaseWrapper
    from gapper.core.test_result import TestResult


class CustomTestFn(Protocol):
    def __call__[
        T
    ](self, param: TestCaseWrapper, proxy: TestResult, expected: T, actual: T) -> None:
        ...


class CustomEqualityCheckFn(Protocol):
    def __call__[T](self, expected: T, actual: T, msg: str | None = None) -> None:
        ...


def generate_custom_input(input_list: Iterable[str]) -> Callable[[Any], str]:
    """Generate a custom input function for a test case."""
    _iterator = iter(input_list)

    def _custom_input(*args: Any) -> str:
        """Mimic `input`'s behavior.

        Read a string from standard input.  The trailing newline is stripped.

        The prompt string, if given, is printed to standard output without a
        trailing newline before reading input.

        If the user hits EOF (*nix: Ctrl-D, Windows: Ctrl-Z+Return), raise EOFError.
        On *nix systems, readline is used if available.
        """
        print(*(str(arg) for arg in args), end="")
        return next(_iterator).rstrip("\n")

    return _custom_input


class CaptureStdout:
    def __init__(self, capture: bool) -> None:
        self._capture: bool = capture
        self._capture_device: redirect_stdout[StringIO] | None = None
        self._io_device: StringIO | None = None

    def __enter__(self) -> Self:
        if self._capture:
            self._io_device = StringIO()
            self._capture_device = redirect_stdout(self._io_device)
            self._capture_device.__enter__()
        return self

    def __exit__(self, *args) -> None:
        if self._capture and self._capture_device:
            return self._capture_device.__exit__(*args)
        return None

    @property
    def value(self) -> str | None:
        if self._capture and self._io_device:
            return self._io_device.getvalue()
        else:
            return None


class ModuleLoader:
    @staticmethod
    def _load_module_spec_and_module(
        path: Path, name: str = "module", exec_mod: bool = False
    ) -> Tuple[ModuleSpec, ModuleType]:
        spec = importlib.util.spec_from_file_location(name, path)

        if spec is None:
            # Based on inspection of the source, I'm not certain how this can happen, but my
            # type checker insists it can. This seems like the most reasonable error to
            # raise.
            raise FileNotFoundError(
                f"Cannot find module spec with path {path.absolute()}"
            )

        md = importlib.util.module_from_spec(spec)

        if exec_mod:
            spec.loader.exec_module(md)

        return spec, md

    @staticmethod
    def _load_symbol_from_module(md: ModuleType, symbol: str) -> Any:
        return getattr(md, symbol)
