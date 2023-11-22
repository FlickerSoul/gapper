from typing import Generator

import pytest
from gapper.core.errors import InternalError, TestFailedError
from gapper.core.hook import HookBase


class TestHook(HookBase):
    _hook_type = "test_hook"


def test_generator_not_exhausted() -> None:
    def hook_fn(*_, **__) -> Generator[None, None, None]:
        yield
        yield

    hb = TestHook(hook_fn=hook_fn, as_test_case=False)
    hb.run()

    with pytest.raises(InternalError, match="Generator not exhausted"):
        hb.tear_down()


def test_generator_exhausted() -> None:
    def hook_fn(*_, **__) -> Generator[None, None, None]:
        yield

    hb = TestHook(hook_fn=hook_fn, as_test_case=False)
    hb.run()
    hb.tear_down()


def test_function_tear_down() -> None:
    def hook_fn(*_, **__) -> None:
        pass

    hb = TestHook(hook_fn=hook_fn, as_test_case=False)
    hb.run()
    hb.tear_down()


def test_assertion_error_catch() -> None:
    def hook_fn(*_, **__) -> None:
        assert False, "Test Failed"

    hb = TestHook(hook_fn=hook_fn)
    test_result = hb.run()
    assert len(test_result.errors) == 1
    assert isinstance(test_result.errors[0], TestFailedError)
