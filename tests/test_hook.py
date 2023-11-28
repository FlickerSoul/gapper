from dataclasses import dataclass, field
from typing import Generator

import pytest
from gapper.core.errors import InternalError, TestFailedError
from gapper.core.hook import HookBase
from gapper.core.test_result import TestResult
from gapper.core.types import HookDataBase


class TestHook(HookBase):
    _hook_type = "test_hook"


@dataclass
class TestHookData(HookDataBase):
    result_proxy: TestResult = field(default=None)


def test_generator_not_exhausted() -> None:
    def hook_fn(data) -> Generator[None, None, None]:
        yield
        yield

    hb = TestHook(hook_fn=hook_fn, as_test_case=False)
    hb.run(TestHookData())

    with pytest.raises(InternalError, match="Generator not exhausted"):
        hb.tear_down()


def test_generator_exhausted() -> None:
    def hook_fn(*_, **__) -> Generator[None, None, None]:
        yield

    hb = TestHook(hook_fn=hook_fn, as_test_case=False)
    hb.run(TestHookData())
    hb.tear_down()


def test_function_tear_down() -> None:
    def hook_fn(*_, **__) -> None:
        pass

    hb = TestHook(hook_fn=hook_fn, as_test_case=False)
    hb.run(TestHookData())
    hb.tear_down()


def test_assertion_error_catch() -> None:
    def hook_fn(*_, **__) -> None:
        assert False, "Test Failed"

    hb = TestHook(hook_fn=hook_fn)
    test_result = hb.run(TestHookData())
    assert len(test_result.errors) == 1
    assert isinstance(test_result.errors[0], TestFailedError)
