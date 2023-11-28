"""The module contains the test case (parameter) support classes and functions."""
from __future__ import annotations

import warnings
from dataclasses import asdict, dataclass
from enum import Enum
from functools import partial
from itertools import product
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Iterable,
    List,
    Sequence,
    overload,
)

__all__ = [
    "tc",
    "tcs",
    "TestParam",
    "TestParamBundle",
    "ParamExtractor",
    "test_case",
    "param",
    "test_cases",
    "test_cases_params",
    "test_cases_param_iter",
    "test_cases_zip",
    "test_cases_product",
    "test_cases_singular_params",
    "test_cases_singular_param_iter",
]

from gapper.core.errors import InternalError

if TYPE_CHECKING:
    from gapper.core.problem import Problem
    from gapper.core.problem.problem_def import ProbInputType, ProbOutputType
    from gapper.core.types import (
        CustomEqualityCheckFn,
        CustomTestFn,
        PostHookFn,
        PreHookFn,
    )


class GapReservedKeywords(Enum):
    """Reserved keywords for gap."""

    gap_expect = "gap_expect"
    gap_expect_stdout = "gap_expect_stdout"
    gap_hidden = "gap_hidden"
    gap_name = "gap_name"
    gap_weight = "gap_weight"
    gap_max_score = "gap_max_score"
    gap_extra_points = "gap_extra_points"
    gap_override_check = "gap_override_check"
    gap_easy_context = "gap_easy_context"
    gap_override_test = "gap_override_test"
    gap_pre_hooks = "gap_pre_hooks"
    gap_post_hooks = "gap_post_hooks"
    gap_description = "gap_description"
    gap_is_pipeline = "gap_is_pipeline"


@dataclass
class ParamInfo:
    gap_expect: Any | None = None
    gap_expect_stdout: str | None = None
    gap_hidden: bool = False
    gap_name: str | None = None
    gap_extra_points: float | None = None
    gap_override_check: CustomEqualityCheckFn | None = None
    gap_easy_context: bool = False
    gap_override_test: CustomTestFn | None = None
    gap_pre_hooks: List[PreHookFn] | PreHookFn | None = None
    gap_post_hooks: List[PostHookFn] | PostHookFn | None = None
    gap_description: str | Iterable[str] | None = None
    gap_is_pipeline: bool = False
    gap_max_score: float | None = None
    gap_weight: int | None = None

    def update(self, new_info: Dict[str, Any]) -> None:
        for key, value in new_info.items():
            if hasattr(self, key):
                setattr(self, key, value)


class ParamExtractor:
    """A class to extract the gap test parameter."""

    def __init__(self, kwargs: Dict[str, Any]) -> None:
        """Initialize the gap test parameter."""
        gap_params = type(self).extra_gap_info(kwargs)
        self._param_info = type(self)._select_param_info(gap_params)

    @property
    def param_info(self) -> ParamInfo:
        """Return the parameter information."""
        return self._param_info

    @classmethod
    def extra_gap_info(
        cls, kwargs: Dict[str, Any], check_residue: bool = True
    ) -> Dict[str, Any]:
        gap_kwargs = {
            k.value: kwargs.pop(k.value)
            for k in GapReservedKeywords
            if k.value in kwargs
        }

        if check_residue:
            if caught_residue := cls.check_gap_kwargs_residue(kwargs):
                raise ValueError(f"Unknown gap keyword arguments: {caught_residue}")

        return gap_kwargs

    @staticmethod
    def _select_param_info(kwargs: Dict[str, Any]) -> ParamInfo:
        """Select the parameter information to fill in."""
        if (
            kwargs.get(GapReservedKeywords.gap_max_score.value, None) is not None
            and kwargs.get(GapReservedKeywords.gap_weight.value, None) is not None
        ):
            raise ValueError("Cannot specify both gap_max_score and gap_weight.")
        else:
            return ParamInfo(**kwargs)

    @staticmethod
    def check_gap_kwargs_residue(kwargs: Dict[str, Any]) -> List[str]:
        """Check if there are any residue gap kwargs.

        :param kwargs: The keyword arguments to check.
        """
        caught: List[str] = []

        for kwarg in kwargs.keys():
            if kwarg.startswith("gap_"):
                caught.append(kwarg)

        return caught

    def update_gap_kwargs(self, **kwargs: Any) -> None:
        """Update the gap kwargs with a set of kwargs.

        :param kwargs: The keyword arguments to be pushed into the param_info.
        """
        self._param_info.update(kwargs)

    def __eq__(self, other: ParamExtractor) -> bool:
        """Check if the test parameter is equal to another test parameter."""
        if isinstance(other, ParamExtractor):
            return self.param_info == other.param_info
        return False


class _BoundTestParam(partial):
    __slots__ = ()

    @overload
    def __new__(
        cls,
        *args: Any,
        gap_expect: Any | Sequence[Any] | None = None,
        gap_expect_stdout: str | Sequence[str] | None = None,
        gap_hidden: bool | Sequence[bool] = False,
        gap_name: str | Sequence[str] | None = None,
        gap_extra_points: float | Sequence[float] | None = None,
        gap_override_check: CustomEqualityCheckFn
        | Sequence[CustomEqualityCheckFn]
        | None = None,
        gap_easy_context: bool | Sequence[bool] = False,
        gap_override_test: CustomTestFn | Sequence[CustomTestFn] | None = None,
        gap_post_hooks: List[List[PostHookFn]]
        | List[PostHookFn]
        | PostHookFn
        | None = None,
        gap_pre_hooks: List[List[PreHookFn]]
        | List[PreHookFn]
        | PreHookFn
        | None = None,
        gap_description: str | Iterable[str] | Sequence[Iterable[str]] | None = None,
        gap_is_pipeline: bool | Sequence[bool] = False,
        gap_max_score: float | Sequence[float] | None = None,
        gap_weight: float | Sequence[float] | None = None,
        **kwargs: Any,
    ) -> None:
        ...

    def __new__(cls, *args, **kwargs) -> _BoundTestParam:
        return super().__new__(cls, TestParam, *args, **kwargs)


class TestParam(ParamExtractor):
    """A class to represent a test case (parameter). Will be used as @test_case() decorator.

    :cvar pipeline: specify test case using pipeline actions.
    """

    pipeline: ClassVar[partial[TestParam]]
    bind = _BoundTestParam

    @overload
    def __init__(
        self,
        *args: Any,
        gap_expect: Any | None = None,
        gap_expect_stdout: str | None = None,
        gap_hidden: bool = False,
        gap_name: str | None = None,
        gap_extra_points: float | None = None,
        gap_override_check: CustomEqualityCheckFn | None = None,
        gap_easy_context: bool = False,
        gap_override_test: CustomTestFn | None = None,
        gap_pre_hooks: List[PreHookFn] | PreHookFn | None = None,
        gap_post_hooks: List[PostHookFn] | PostHookFn | None = None,
        gap_description: str | Iterable[str] | None = None,
        gap_is_pipeline: bool = False,
        gap_max_score: float | None = None,
        **kwargs,
    ) -> None:
        """Initialize the gap test parameter (test_case).

        :param args: The arguments for the test parameter.
        :param gap_expect: The expected output of the test case.
        :param gap_expect_stdout: The expected stdout of the test case.
        :param gap_hidden: Whether the test case is hidden.
        :param gap_name: The name of the test case.
        :param gap_extra_points: The extra credit of the test case.
        :param gap_override_check: The custom equality check function.
        :param gap_easy_context: Whether to use context directly in gap override tests.
        :param gap_override_test: The custom test function.
        :param gap_pre_hooks: The custom functions run before tests.
        :param gap_post_hooks: The custom functions run after tests.
        :param gap_description: The description of the test case.
        :param gap_is_pipeline: Whether the test case is a pipeline.
        :param gap_max_score: The max score of the test case. This and gap_weight cannot be specified as the same ti
        :param kwargs: The keyword arguments for the test parameter, including kwargs.
        """

    @overload
    def __init__(
        self,
        *args: Any,
        gap_expect: Any | None = None,
        gap_expect_stdout: str | None = None,
        gap_hidden: bool = False,
        gap_name: str | None = None,
        gap_extra_points: float | None = None,
        gap_override_check: CustomEqualityCheckFn | None = None,
        gap_easy_context: bool = False,
        gap_override_test: CustomTestFn | None = None,
        gap_pre_hooks: List[PreHookFn] | PreHookFn | None = None,
        gap_post_hooks: List[PostHookFn] | PostHookFn | None = None,
        gap_description: str | Iterable[str] | None = None,
        gap_is_pipeline: bool = False,
        gap_weight: float | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the gap test parameter (test_case).

        :param args: The arguments for the test parameter.
        :param gap_expect: The expected output of the test case.
        :param gap_expect_stdout: The expected stdout of the test case.
        :param gap_hidden: Whether the test case is hidden.
        :param gap_name: The name of the test case.
        :param gap_extra_points: The extra credit of the test case.
        :param gap_override_check: The custom equality check function.
        :param gap_easy_context: Whether to use context directly in gap override tests.
        :param gap_override_test: The custom test function.
        :param gap_pre_hooks: The custom functions run before tests.
        :param gap_post_hooks: The custom functions run after tests.
        :param gap_description: The description of the test case.
        :param gap_is_pipeline: Whether the test case is a pipeline.
        :param gap_weight: The weight of the test case. This and gap_max_score cannot be specified as the same time.
        :param kwargs: The keyword arguments for the test parameter, including kwargs.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the gap test parameter (test_case).

        :param args: The arguments for the test parameter.
        :param kwargs: The keyword arguments for the test parameter, including kwargs.
        """
        super().__init__(kwargs)
        self._args = args
        self._kwargs = kwargs

    def __call__[T: Problem[ProbInputType, ProbOutputType]](self, prob: T) -> T:
        """Make itself to be a decorator."""
        return self.register_test_param(prob)

    def register_test_param[T: Problem[ProbInputType, ProbOutputType]](
        self, prob: T
    ) -> T:
        """Register the test parameter to the problem."""
        prob.add_test_parameter(self)
        return prob

    @property
    def args(self) -> tuple[Any, ...]:
        """Return the arguments of the test parameter."""
        return self._args

    @args.setter
    def args(self, args: tuple[Any, ...]) -> None:
        """Set the arguments of the test parameter."""
        self._args = args

    @property
    def kwargs(self) -> dict[str, Any]:
        """Return the keyword arguments of the test parameter."""
        return self._kwargs

    @kwargs.setter
    def kwargs(self, kwargs: dict[str, Any]) -> None:
        """Set the keyword arguments of the test parameter."""
        self._kwargs = kwargs

    def format(self, with_gap_kwargs: bool = False) -> str:
        """Format the test parameter."""
        args = self.args

        if with_gap_kwargs:
            kwargs = {**self.kwargs, **asdict(self.param_info)}
        else:
            kwargs = self.kwargs

        args_format = ", ".join(str(arg) for arg in args)
        kwargs_format = ", ".join(f"{kwarg}={value}" for kwarg, value in kwargs.items())

        if args_format:
            if kwargs_format:
                return f"({args_format}, {kwargs_format})"
            else:
                return f"({args_format})"
        else:
            return f"({kwargs_format})"

    def __eq__(self, other: TestParam) -> bool:
        """Check if the test parameter is equal to another test parameter.

        Two test parameters are equal if their args, kwargs, and params_info are equal.

        :param other: The other test parameter to compare with.
        """
        if isinstance(other, TestParam):
            return (
                self.args == other.args
                and self.kwargs == other.kwargs
                and super().__eq__(other)
            )

        return False

    def __repr__(self) -> str:
        """Return the representation of the test parameter."""
        return f"param{self.format(with_gap_kwargs=True)}"


tc = TestParam
test_case = TestParam
param = TestParam
test_case.pipeline = partial(TestParam, gap_is_pipeline=True)


class _BoundTestParamBundle(partial):
    __slots__ = ("params", "param_iter", "singular_params", "singular_param_iter")

    @overload
    def __new__(
        cls,
        *args: Any,
        gap_expect: Any | Sequence[Any] | None = None,
        gap_expect_stdout: str | Sequence[str] | None = None,
        gap_hidden: bool | Sequence[bool] = False,
        gap_name: str | Sequence[str] | None = None,
        gap_extra_points: float | Sequence[float] | None = None,
        gap_override_check: CustomEqualityCheckFn
        | Sequence[CustomEqualityCheckFn]
        | None = None,
        gap_easy_context: bool | Sequence[bool] = False,
        gap_override_test: CustomTestFn | Sequence[CustomTestFn] | None = None,
        gap_post_hooks: List[List[PostHookFn]]
        | List[PostHookFn]
        | PostHookFn
        | None = None,
        gap_pre_hooks: List[List[PreHookFn]]
        | List[PreHookFn]
        | PreHookFn
        | None = None,
        gap_description: str | Iterable[str] | Sequence[Iterable[str]] | None = None,
        gap_is_pipeline: bool | Sequence[bool] = False,
        gap_max_score: float | Sequence[float] | None = None,
        gap_weight: float | Sequence[float] | None = None,
        gap_params: bool = False,
        gap_param_iter: bool = False,
        gap_singular_params: bool = False,
        gap_singular_param_iter: bool = False,
        **kwargs: Any,
    ) -> None:
        ...

    def __new__(cls, *args, **kwargs) -> _BoundTestParamBundle:
        obj = super().__new__(cls, TestParamBundle, *args, **kwargs)
        obj.params = partial(obj, gap_params=True)
        obj.param_iter = partial(obj, gap_param_iter=True)
        obj.singular_params = partial(obj, gap_singular_params=True)
        obj.singular_param_iter = partial(obj, gap_singular_param_iter=True)

        return obj


class TestParamBundle:
    """A class to represent a test parameter bundle (test_cases). Will be used as @test_cases() decorator.

    :cvar params: specify test cases using parameters.
    :cvar param_iter: specify test cases using parameter iterators.
    :cvar singular_params: specify test cases using singular parameters.
    :cvar singular_param_iter: specify test cases using singular parameter iterators.
    :cvar zip: specify test cases using zip.
    :cvar product: specify test cases using product.
    """

    params: ClassVar[partial[TestParamBundle]]
    param_iter: ClassVar[partial[TestParamBundle]]
    zip: ClassVar[partial[TestParamBundle]]
    product: ClassVar[partial[TestParamBundle]]
    singular_params: ClassVar[partial[TestParamBundle]]
    singular_param_iter: ClassVar[partial[TestParamBundle]]

    bind = _BoundTestParamBundle

    @overload
    def __init__(
        self,
        *args: Any,
        gap_expect: Any | Sequence[Any] | None = None,
        gap_expect_stdout: str | Sequence[str] | None = None,
        gap_hidden: bool | Sequence[bool] = False,
        gap_name: str | Sequence[str] | None = None,
        gap_extra_points: float | Sequence[float] | None = None,
        gap_override_check: CustomEqualityCheckFn
        | Sequence[CustomEqualityCheckFn]
        | None = None,
        gap_easy_context: bool | Sequence[bool] = False,
        gap_override_test: CustomTestFn | Sequence[CustomTestFn] | None = None,
        gap_post_hooks: List[List[PostHookFn]]
        | List[PostHookFn]
        | PostHookFn
        | None = None,
        gap_pre_hooks: List[List[PreHookFn]]
        | List[PreHookFn]
        | PreHookFn
        | None = None,
        gap_description: str | Iterable[str] | Sequence[Iterable[str]] | None = None,
        gap_is_pipeline: bool | Sequence[bool] = False,
        gap_max_score: float | Sequence[float] | None = None,
        gap_params: bool = False,
        gap_param_iter: bool = False,
        gap_singular_params: bool = False,
        gap_singular_param_iter: bool = False,
        **kwargs,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *args: Any,
        gap_expect: Any | Sequence[Any] | None = None,
        gap_expect_stdout: str | Sequence[str] | None = None,
        gap_hidden: bool | Sequence[bool] = False,
        gap_name: str | Sequence[str] | None = None,
        gap_extra_points: float | Sequence[float] | None = None,
        gap_override_check: CustomEqualityCheckFn
        | Sequence[CustomEqualityCheckFn]
        | None = None,
        gap_easy_context: bool | Sequence[bool] = False,
        gap_override_test: CustomTestFn | Sequence[CustomTestFn] | None = None,
        gap_pre_hooks: List[List[PreHookFn]]
        | List[PreHookFn]
        | PreHookFn
        | None = None,
        gap_post_hooks: List[List[PostHookFn]]
        | List[PostHookFn]
        | PostHookFn
        | None = None,
        gap_description: str | Iterable[str] | Sequence[Iterable[str]] | None = None,
        gap_is_pipeline: bool | Sequence[bool] = False,
        gap_weight: float | Sequence[float] | None = None,
        gap_params: bool = False,
        gap_param_iter: bool = False,
        gap_singular_params: bool = False,
        gap_singular_param_iter: bool = False,
        **kwargs: Any,
    ) -> None:
        ...

    def __init__(
        self,
        *args: Iterable[Any] | Any,
        gap_product: bool = False,
        gap_zip: bool = False,
        gap_params: bool = False,
        gap_param_iter: bool = False,
        gap_singular_params: bool = False,
        gap_singular_param_iter: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize the test parameter bundle (test_cases).

        :param args: The arguments for the test parameter bundle.
        :param gap_product: Whether to take the cartesian product of the arguments.
            .. deprecated::
                Use params, param_iter, singular_params, singular_param_iter instead.
        :param gap_zip: Whether to zip the arguments.
            .. deprecated::
                Use params, param_iter, singular_params, singular_param_iter instead.
        :param gap_params: Whether to parse the arguments as parameters.
        :param gap_param_iter: Whether to parse the argument as parameter iterators.
        :param gap_singular_params: Whether to parse the arguments as singular parameters.
        :param gap_singular_param_iter: Whether to parse the arguments as singular parameter iterators.
        :param kwargs: The keyword arguments for the test parameter bundle.
            .. seealso::
                :class:`gapper.core.test_parameter.TestParam`
            .. seealso::
                :class:`gapper.core.test_parameter.ParamExtractor`
        """
        if (
            gap_params
            + gap_param_iter
            + gap_zip
            + gap_product
            + gap_singular_params
            + gap_singular_param_iter
        ) != 1:
            raise ValueError(
                "Exactly many of gap_product, gap_zip, or gap_params are True. "
                "Only 1 of the flags is allowed. \n"
                f"You got: "
                f"gap_product={gap_product}, gap_zip={gap_zip}, "
                f"gap_params={gap_params}, gap_singular_params={gap_singular_params}"
            )

        if gap_product:
            raise warnings.warn("gap_product is deprecated.")
        if gap_zip:
            raise warnings.warn("gap_zip is deprecated.")

        # pop gap keywords out
        gap_kwargs_dict = ParamExtractor.extra_gap_info(kwargs)

        if gap_params:
            self.final_params: List[TestParam] = type(self).parse_params(
                *args, **kwargs
            )
        elif gap_param_iter:
            self.final_params = type(self).parse_param_iter(*args, **kwargs)
        elif gap_singular_params:
            self.final_params = type(self).parse_singular_params(*args, **kwargs)
        elif gap_singular_param_iter:
            self.final_params = type(self).parse_singular_param_iter(*args, **kwargs)
        elif gap_zip or gap_product:
            self.final_params = type(self).parse_zip_or_product(
                *args, gap_zip=gap_zip, gap_product=gap_product, **kwargs
            )
        else:
            raise InternalError("TestParamBundle.__init__ should not reach here.")

        type(self).add_gap_kwargs(gap_kwargs_dict, self.final_params)

    @staticmethod
    def parse_param_iter(*args: Iterable[Any], **kwargs: Any) -> List[TestParam]:
        """Parse the param_iter args to param sequence."""
        if kwargs:
            raise ValueError(
                "gap_param_iter=True ignores non-gap kwargs. "
                "Please use `param()` directive to assist specifying kwargs."
            )

        if len(args) != 1:
            raise ValueError("gap_param_iter=True only accepts 1 iterable argument.")

        arg_iter = args[0]

        return list(
            arg if isinstance(arg, TestParam) else param(*arg) for arg in arg_iter
        )

    @staticmethod
    def parse_params(*args: Iterable[Any], **kwargs: Any) -> List[TestParam]:
        """Parse the parameters for param sequence."""
        if kwargs:
            raise ValueError(
                "gap_params=True ignores non-gap kwargs. "
                "Please use `param()` directive to assist specifying kwargs."
            )

        return list(arg if isinstance(arg, TestParam) else param(*arg) for arg in args)

    @staticmethod
    def parse_singular_params(*args: Iterable[Any], **kwargs: Any) -> List[TestParam]:
        """Parse the parameters for param sequence."""
        if kwargs:
            raise ValueError(
                "gap_singular_params=True ignores non-gap kwargs. "
                "Please use `param()` directive to assist specifying kwargs."
            )

        return list(arg if isinstance(arg, TestParam) else param(arg) for arg in args)

    @staticmethod
    def parse_singular_param_iter(
        *args: Iterable[Any], **kwargs: Any
    ) -> List[TestParam]:
        """Parse the singular_param_iter args to param sequence."""
        if kwargs:
            raise ValueError(
                "gap_singular_param_iter=True ignores non-gap kwargs. "
                "Please use `param()` directive to assist specifying kwargs."
            )

        if len(args) != 1:
            raise ValueError(
                "gap_singular_param_iter=True only accepts 1 iterable argument."
            )

        arg_iter = args[0]

        return list(
            arg if isinstance(arg, TestParam) else param(arg) for arg in arg_iter
        )

    @staticmethod
    def parse_zip_or_product(
        *args: Iterable[Any],
        gap_product: bool = False,
        gap_zip: bool = False,
        **kwargs: Any,
    ) -> List[TestParam]:
        """Parse parameters for zip or product.

        :deprecated: Use params, param_iter, singular_params, singular_param_iter instead.
        """
        if not gap_zip ^ gap_product:
            raise ValueError("exactly one of gap_zip or gap_product must be True")
        combinator = product if gap_product else zip

        # ok so if the combinator is product
        # we are taking the cartesian product for all args and kwargs
        # and if the combinator is zip,
        # we are zipping all the args and kwargs, if there are any
        combined_args = list(combinator(*args))
        combined_kwargs = list(combinator(*kwargs.values()))

        # ======= validation checks =======
        if combinator is zip:
            # create empty args for zip if there are no args
            if combined_args and combined_kwargs:
                if len(combined_args) != len(combined_kwargs):
                    raise ValueError(
                        'length of "args" and "kwargs" must match in zip mode'
                    )
            elif combined_args:
                combined_kwargs = [()] * len(combined_args)
            elif combined_kwargs:
                combined_args = [()] * len(combined_kwargs)

        all_args_and_kwargs = list(combinator(combined_args, combined_kwargs))

        # ======= zipping all the args together =======
        return list(
            param(*curr_args, **dict(zip(kwargs.keys(), curr_kwargs)))
            for (curr_args, curr_kwargs) in all_args_and_kwargs
        )

    @staticmethod
    def add_gap_kwargs(
        gap_kwargs: Dict[str, Any], final_params: List[TestParam]
    ) -> None:
        """Add gap_kwargs to the finalized parameters."""
        # process gap input type
        for gap_kwarg_key, gap_kwarg_value in gap_kwargs.items():
            if isinstance(gap_kwarg_value, Iterable) and not isinstance(
                gap_kwarg_value, str
            ):
                gap_kwargs[gap_kwarg_key] = list(gap_kwarg_value)
            else:
                gap_kwargs[gap_kwarg_key] = [gap_kwarg_value] * len(final_params)

        # validate gap input type
        if not all(
            len(gap_kwarg_value) == len(final_params)
            for gap_kwarg_value in gap_kwargs.values()
        ):
            # the length of the kwargs should be equal to the number of test cases
            # i.e. the length of the combined args
            raise ValueError(
                f"all gap_ keyword args must have the same length as the test cases, "
                f"which is {len(final_params)}"
            )

        # the gap kwargs list we want
        gap_kwargs_list: List[Dict[str, Any]] = [
            dict(zip(gap_kwargs.keys(), gap_kwarg_value))
            for gap_kwarg_value in zip(*gap_kwargs.values())
        ]

        if not gap_kwargs_list:
            # generate default gap kwargs dict if there are no gap kwargs
            gap_kwargs_list = [{} for _ in final_params]

        for final_param, kwargs in zip(final_params, gap_kwargs_list):
            final_param.update_gap_kwargs(**kwargs)

    def __call__(
        self, prob: Problem[ProbInputType, ProbOutputType]
    ) -> Problem[ProbInputType, ProbOutputType]:
        """Generate the test cases as a decorator."""
        for final_param in self.final_params:
            prob = final_param.register_test_param(prob)

        return prob


tcs = TestParamBundle
test_cases = TestParamBundle
test_cases_params = partial(test_cases, gap_params=True)
test_cases_param_iter = partial(test_cases, gap_param_iter=True)
test_cases_zip = partial(test_cases, gap_zip=True)
test_cases_product = partial(test_cases, gap_product=True)
test_cases_singular_params = partial(test_cases, gap_singular_params=True)
test_cases_singular_param_iter = partial(test_cases, gap_singular_param_iter=True)
test_cases.params = test_cases_params
test_cases.param_iter = test_cases_param_iter
test_cases.product = test_cases_product
test_cases.zip = test_cases_zip
test_cases.singular_params = test_cases_singular_params
test_cases.singular_param_iter = test_cases_singular_param_iter
