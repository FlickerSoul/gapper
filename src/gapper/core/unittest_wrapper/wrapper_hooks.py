from __future__ import annotations

from gapper.core.hook import HookBase, HookTypes
from gapper.core.test_result import TestResult


class PreTest(HookBase):
    def _run(
        self,
        *args,
        result_proxy: TestResult | None,
        **kwargs,
    ) -> None:
        super()._run(
            kwargs["case"], result_proxy, kwargs["solution"], kwargs["submission"]
        )

    def __repr__(self) -> str:
        return f"PreTestsHook(hook_fn={self.hook_fn})"


pre_test = PreTest


class PostTest(HookBase):
    _hook_type = HookTypes.POST_TEST

    def _run(
        self,
        *args,
        result_proxy: TestResult | None,
        **kwargs,
    ) -> None:
        super()._run(
            kwargs["case"],
            result_proxy,
            kwargs["solution"],
            kwargs["submission"],
            kwargs["expected_results"],
            kwargs["actual_results"],
        )

    def __repr__(self) -> str:
        return f"PostTestHook(hook_fn={self.hook_fn})"


post_test = PostTest
