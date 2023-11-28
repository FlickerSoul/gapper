"""Utility functions and classes for the core module."""
from __future__ import annotations

import importlib.util
import logging
from contextlib import redirect_stdout
from copy import copy
from functools import update_wrapper
from importlib.machinery import ModuleSpec
from io import StringIO
from pathlib import Path
from types import FunctionType, ModuleType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    Self,
    Tuple,
)

if TYPE_CHECKING:
    pass


_util_logger = logging.getLogger("gapper.core.utils")


def generate_custom_input(input_list: Iterable[str]) -> Callable[[Any], str]:
    """Generate a custom input function for a test case.

    :param input_list: The list of inputs to be used.
    :return: The custom input function.
    """
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
    """A context manager to capture stdout."""

    def __init__(self, capture: bool) -> None:
        """Create a context manager to capture stdout.

        :param capture: Whether to capture stdout.
        """
        self._capture: bool = capture
        self._capture_device: redirect_stdout[StringIO] | None = None
        self._io_device: StringIO | None = None

    def __enter__(self) -> Self:
        """Enter as a context manager."""
        if self._capture:
            self._io_device = StringIO()
            self._capture_device = redirect_stdout(self._io_device)
            self._capture_device.__enter__()
        return self

    def __exit__(self, *args) -> None:
        """Exit as the context manager."""
        if self._capture and self._capture_device:
            return self._capture_device.__exit__(*args)
        return None

    @property
    def value(self) -> str | None:
        """The captured stdout."""
        if self._capture and self._io_device:
            return self._io_device.getvalue()
        else:
            return None


class ModuleLoader:
    """A mixin class to load modules from files."""

    @staticmethod
    def _load_module_spec_and_module(
        path: Path, name: str = "module", exec_mod: bool = False
    ) -> Tuple[ModuleSpec, ModuleType]:
        """Load a module spec and module from a file.

        :param path: The path to the file.
        :param name: The name of the module to be registered.
        :param exec_mod: Whether to execute the module.
        :return: The module spec and the module.
        """
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
        """Load a symbol from a module."""
        return getattr(md, symbol)


def apply_context_on_fn[T: FunctionType](f: T, context: dict[str, Any]) -> T:
    """Apply a context on a function.

    :param f: The function to apply context on.
    :param context: The context to be applied.
    :return: The function with context applied.
    """
    if not isinstance(f, FunctionType):
        raise TypeError(f"Cannot apply context on {f} because it is not a function")

    _util_logger.debug(f"Applying context {context} on function {f}")

    _util_logger.debug("check duplicates in local variables")
    for local_var_name in f.__code__.co_varnames:
        if local_var_name in context:
            raise ValueError(
                f'Cannot apply context value of "{local_var_name}" because it is already defined in the function'
            )

    # update closure with context
    _util_logger.debug("Gathering closure with context")
    closure_mod: Dict[str, int] = {}
    if f.__closure__ is not None:
        for index, closure_var_name in enumerate(f.__code__.co_freevars):
            if closure_var_name in context:
                _util_logger.debug(
                    f'Found closure variable "{closure_var_name}" ({index}) in context'
                )
                closure_mod[closure_var_name] = index
            else:
                _util_logger.debug(
                    f'Cannot find closure variable "{closure_var_name}" in context, skipped"'
                )

    g = FunctionType(
        f.__code__,
        {
            **f.__globals__,
            **{
                c_name: c_val
                for c_name, c_val in context.items()
                if c_name not in closure_mod
            },
        },  # copy globals and update with context
        name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__,
    )
    g = update_wrapper(g, f)
    g.__kwdefaults__ = copy(f.__kwdefaults__)

    _util_logger.debug(f"Function {f} copied")

    for c_name, c_pos in closure_mod.items():
        _util_logger.debug(f"Updating closure variable {c_name} at position {c_pos}")
        g.__closure__[c_pos].cell_contents = context[c_name]

    _util_logger.debug("Closure updated")

    return g
