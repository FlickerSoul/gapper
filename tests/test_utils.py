import re

import pytest
from gapper.core.utils import apply_context_on_fn


def test_reject_callable() -> None:
    class Call:
        def __call__(self, *args, **kwargs):
            pass

    call = Call()

    with pytest.raises(
        TypeError, match=r"Cannot apply context on .* because it is not a function"
    ):
        apply_context_on_fn(call, {"a": 1, "b": 2})


def test_reject_if_has_locals() -> None:
    def fn():
        a = 1

    with pytest.raises(
        ValueError,
        match=re.escape(
            'Cannot apply context value of "a" because it is already defined in the function'
        ),
    ):
        apply_context_on_fn(fn, {"a": 1})


def test_closure() -> None:
    def outer():
        b: int

        def inner():
            return b

        return inner

    f = outer()

    g = apply_context_on_fn(f, {"b": 1})

    assert g() == 1


global_val: int


def test_global() -> None:
    def f():
        return global_val

    g = apply_context_on_fn(f, {"global_val": 1})

    assert g() == 1
