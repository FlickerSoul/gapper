from __future__ import annotations

import abc
import enum
import inspect
from collections import defaultdict
from typing import TYPE_CHECKING, Callable, ClassVar, Dict, Generator, List

from gapper.core.errors import InternalError, TestFailedError
from gapper.core.test_parameter import ParamExtractor
from gapper.core.test_result import TestResult
from gapper.core.types import HookDataBase

if TYPE_CHECKING:
    from gapper.core.problem import Problem


class HookTypes(enum.Enum):
    """The types of hooks."""

    PRE_TESTS = "pre_tests"
    POST_TESTS = "post_tests"
    PRE_HOOK = "pre_hook"
    POST_HOOK = "post_hook"


HookFnReturnType = Generator | None


class HookBase[**P, FnType: Callable[P, HookFnReturnType]](ParamExtractor):
    _hook_type: ClassVar[HookTypes]

    def __init__(
        self,
        hook_fn: FnType,
        as_test_case: bool = True,
        **kwargs,
    ) -> None:
        """
        :param hook_fn: The function when the hook is triggered.
        :param as_test_case: Whether to treat the post test as a test case.
            If this is set to True, this hook will incur a TestResult instance to be
            created and will then be used to synthesize the score. Therefore, it will
            also be seen as an entry in gradescope.

            If this is set to False, it will only have side effects and will not be seen
            as an entry in gradescope.
        :param kwargs: gap keyword parameters.
        """
        super().__init__(kwargs)

        self.hook_fn = hook_fn
        self.as_test_case = as_test_case
        self.hook_fn_res: HookFnReturnType | None = None

    def __call__(self, problem: Problem) -> Problem:
        """Add the post test to the problem.

        :param problem: The problem to add the post test to.
        """
        problem.add_hook(self, self._hook_type)
        return problem

    def run[T: HookDataBase](self, data: T) -> TestResult | None:
        if self.as_test_case and data.result_proxy is None:
            data.result_proxy = TestResult(self.hook_fn.__name__)

        self._setup_result(data.result_proxy)

        try:
            self._run(data)
        except AssertionError as e:
            data.result_proxy.add_error(
                TestFailedError(e), set_failed=data.result_proxy.is_pass_status_unset
            )
        except Exception as e:
            data.result_proxy.add_error(
                InternalError(e), set_failed=data.result_proxy.is_pass_status_unset
            )
        else:
            if data.result_proxy and data.result_proxy.is_pass_status_unset:
                data.result_proxy.set_pass_status("passed")

        return data.result_proxy

    def _setup_result(self, result: TestResult | None) -> None:
        if result is None:
            return

        result.set_name(self.param_info.gap_name)
        result.set_extra_points(self.param_info.gap_extra_points)
        if self.param_info.gap_max_score is None and self.param_info.gap_weight is None:
            result.set_default_weight()
        else:
            result.set_max_score(self.param_info.gap_max_score)
            result.set_weight(self.param_info.gap_weight)
        result.set_hidden(self.param_info.gap_hidden)
        if self.param_info.gap_description is not None:
            result.add_description(
                *(
                    [self.param_info.gap_description]
                    if isinstance(self.param_info.gap_description, str)
                    else self.param_info.gap_description
                )
            )

    def _run(self, *args: P.args, **kwargs: P.kwargs) -> None:
        self.hook_fn_res = self.hook_fn(*args, **kwargs)
        self.process_generator()

    def __repr__(self) -> str:
        return f"{type(self)}(hook_fn={self.hook_fn}, as_test_case={self.as_test_case}, **{self.param_info})"

    def process_generator(self) -> None:
        """Process the generator if the hook function returns a generator."""
        if inspect.isgenerator(self.hook_fn_res):
            try:
                next(self.hook_fn_res)
            except Exception as e:
                raise InternalError(
                    f"Facing error running {self._hook_type} hook"
                ) from e

    def tear_down(self) -> None:
        """Tear down the generated generator."""
        if inspect.isgenerator(self.hook_fn_res):
            try:
                next(self.hook_fn_res)
            except StopIteration:
                pass
            except Exception as e:
                raise InternalError(
                    f"Facing error during {self._hook_type} hook teardown of fn {self.hook_fn.__name__}"
                ) from e
            else:
                raise InternalError(
                    f"Generator not exhausted in the {self._hook_type} of fn {self.hook_fn.__name__}"
                )


class HookHolder:
    def __init__(self) -> None:
        self._hooks: Dict[HookTypes, List[HookBase] | None] = defaultdict(lambda: None)

    def get_or_gen_hooks(self, hook_type: HookTypes) -> List[HookBase]:
        """Get or generate the hooks of the given type. The result is guaranteed to be a list.

        :param hook_type: The type of the hooks.
        """
        if self.get_hooks(hook_type) is None:
            self.generate_hooks(hook_type)

        return self._hooks[hook_type]

    def get_hooks(self, hook_type: HookTypes) -> List[HookBase] | None:
        """Get the hooks of the given type.

        :param hook_type: The type of the hooks.
        """
        return self._hooks[hook_type]

    @abc.abstractmethod
    def generate_hooks(self, hook_type: HookTypes) -> None:
        """Generate the hooks of the given type.

        :param hook_type: The type of the hooks.
        """

    @abc.abstractmethod
    def run_hooks(
        self, hook_type: HookTypes, data: HookDataBase
    ) -> List[TestResult] | None:
        """Run the hooks of the given type given args and kwargs.

        :param hook_type: The type of the hooks.
        :param data: The data to be passed to the hooks.
        """

    def tear_down_hooks(self, hook_type: HookTypes) -> None:
        """Tear down the hooks of the given type.

        :param hook_type: The type of the hooks.
        """
        hooks = self.get_hooks(hook_type)
        if hooks is None:
            return

        for hook in hooks:
            hook.tear_down()
