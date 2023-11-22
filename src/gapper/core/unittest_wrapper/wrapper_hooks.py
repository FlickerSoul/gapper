from __future__ import annotations

from gapper.core.hook import HookBase, HookTypes
from gapper.core.test_result import TestResult
from gapper.core.utils import PostHookFn, PreHookFn


class PreHook(HookBase):
    _hook_type = HookTypes.PRE_HOOK

    def __init__(self, hook_fn: PreHookFn, **kwargs) -> None:
        super().__init__(hook_fn, as_test_case=False, **kwargs)

    def _run(
        self,
        *args,
        result_proxy: TestResult | None,
        **kwargs,
    ) -> None:
        super()._run(
            kwargs["case"], result_proxy, kwargs["solution"], kwargs["submission"]
        )


pre_hook = PreHook


class PostHook(HookBase):
    _hook_type = HookTypes.POST_HOOK

    def __init__(self, hook_fn: PostHookFn, **kwargs) -> None:
        super().__init__(hook_fn, as_test_case=False, **kwargs)

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


post_hook = PostHook
