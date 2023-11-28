from __future__ import annotations

from gapper.core.hook import HookBase, HookTypes
from gapper.core.types import PostHookFn, PreHookFn


class PreHook(HookBase):
    _hook_type = HookTypes.PRE_HOOK

    def __init__(self, hook_fn: PreHookFn, **kwargs) -> None:
        super().__init__(hook_fn, as_test_case=False, **kwargs)


pre_hook = PreHook


class PostHook(HookBase):
    _hook_type = HookTypes.POST_HOOK

    def __init__(self, hook_fn: PostHookFn, **kwargs) -> None:
        super().__init__(hook_fn, as_test_case=False, **kwargs)


post_hook = PostHook
