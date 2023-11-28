from __future__ import annotations

from gapper.core.hook import HookBase, HookTypes


class PostTests(HookBase):
    """A decorator for post tests. Will be used as @post_tests() decorator."""

    _hook_type = HookTypes.POST_TESTS


post_tests = PostTests


class PreTests(HookBase):
    _hook_type = HookTypes.PRE_TESTS


pre_tests = PreTests
