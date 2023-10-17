from __future__ import annotations

import warnings
from dataclasses import dataclass
from enum import Enum
from functools import partial
from itertools import product
from typing import (
    Any,
    Callable,
    overload,
    Dict,
    List,
    Iterable,
    TYPE_CHECKING,
    Sequence,
    ClassVar,
    Type,
)

__all__ = [
    "TestParam",
    "TestParamBundle",
    "test_case",
    "param",
    "test_cases",
    "test_cases_params",
    "test_cases_zip",
    "test_cases_product",
    "test_cases_singular_params",
]

from gapper.core.errors import InternalError

if TYPE_CHECKING:
    from gapper.core.problem import Problem, ProbOutputType, ProbInputType
    from gapper.core.utils import CustomTestFn, CustomEqualityCheckFn


class GapReservedKeywords(Enum):
    """Reserved keywords for aga."""

    gap_expect = "gap_expect"
    gap_expect_stdout = "gap_expect_stdout"
    gap_hidden = "gap_hidden"
    gap_name = "gap_name"
    gap_weight = "gap_weight"
    gap_value = "gap_value"
    gap_extra_credit = "gap_extra_credit"
    gap_override_check = "gap_override_check"
    gap_override_test = "gap_override_test"
    gap_description = "gap_description"
    gap_is_pipeline = "gap_is_pipeline"


@dataclass
class ParamInfo:
    gap_expect: Any | None = None
    gap_expect_stdout: str | Sequence[str] | None = None
    gap_hidden: bool = False
    gap_name: str | None = None
    gap_extra_credit: float | None = None
    gap_override_check: CustomEqualityCheckFn | None = None
    gap_override_test: CustomTestFn | None = None
    gap_description: str | None = None
    gap_is_pipeline: bool = False
    gap_score: float | None = None
    gap_weight: int | None = None

    def update(self, new_info: Dict[str, Any]) -> None:
        for key, value in new_info.items():
            if hasattr(self, key):
                setattr(self, key, value)


class ParamExtractor:
    def __init__(self, **kwargs: Any) -> None:
        self._param_info = type(self)._select_param_info(kwargs)

    @property
    def param_info(self) -> ParamInfo:
        return self._param_info

    @staticmethod
    def _select_param_info(kwargs: Dict[str, Any]) -> ParamInfo:
        if (
            kwargs.get("gap_score", None) is not None
            and kwargs.get("gap_weight", None) is not None
        ):
            raise ValueError("Cannot specify both gap_score and gap_weight.")
        elif (
            kwargs.get("gap_score", None) is None
            and kwargs.get("gap_weight", None) is None
        ):
            parameter_info = ParamInfo(**kwargs, gap_weight=1)
        else:
            parameter_info = ParamInfo(**kwargs)

        return parameter_info

    @staticmethod
    def check_gap_kwargs_residue(kwargs: Dict[str, Any]) -> List[str]:
        caught: List[str] = []

        for kwarg in kwargs.keys():
            if kwarg.startswith("gap_"):
                caught.append(kwarg)

        return caught

    def update_gap_kwargs(self, **kwargs: Any) -> None:
        self._param_info.update(kwargs)


class TestParam(ParamExtractor):
    @overload
    def __init__[
        T: Problem[ProbInputType, ProbOutputType]
    ](
        self,
        *args: Any,
        gap_expect: Any | None = None,
        gap_expect_stdout: str | Sequence[str] | None = None,
        gap_hidden: bool = False,
        gap_name: str | None = None,
        gap_extra_credit: float | None = None,
        gap_override_check: CustomEqualityCheckFn | None = None,
        gap_override_test: CustomTestFn | None = None,
        gap_description: str | None = None,
        gap_is_pipeline: bool = False,
        gap_score: float | None = None,
        **kwargs,
    ) -> None:
        ...

    @overload
    def __init__[
        T: Problem[ProbInputType, ProbOutputType]
    ](
        self,
        *args: Any,
        gap_expect: Any | None = None,
        gap_expect_stdout: str | Sequence[str] | None = None,
        gap_hidden: bool = False,
        gap_name: str | None = None,
        gap_extra_credit: float | None = None,
        gap_override_check: CustomEqualityCheckFn | None = None,
        gap_override_test: CustomTestFn | None = None,
        gap_description: str | None = None,
        gap_is_pipeline: bool = False,
        gap_weight: float | None = None,
        **kwargs: Any,
    ) -> None:
        ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            **{
                k.value: kwargs.pop(k.value)
                for k in GapReservedKeywords
                if k.value in kwargs
            }
        )

        if caught_residue := self.check_gap_kwargs_residue(kwargs):
            raise ValueError(f"Unknown keyword arguments: {caught_residue}")

        self._args = args
        self._kwargs = kwargs

    def __call__[T: Problem[ProbInputType, ProbOutputType]](self, prob: T) -> T:
        return self.register_test_param(prob)

    def register_test_param[
        T: Problem[ProbInputType, ProbOutputType]
    ](self, prob: T) -> T:
        prob.add_test_parameter(self)
        return prob

    @property
    def args(self) -> tuple[Any, ...]:
        return self._args

    @property
    def kwargs(self) -> dict[str, Any]:
        return self._kwargs

    def format(self) -> str:
        args_format = ", ".join(str(arg) for arg in self.args)
        kwargs_format = ", ".join(
            f"{kwarg}={value}" for kwarg, value in self.kwargs.items()
        )

        if args_format:
            if kwargs_format:
                return f"({args_format}, {kwargs_format})"
            else:
                return f"({args_format})"
        else:
            return f"({kwargs_format})"

    @classmethod
    def bind_override(
        cls,
        *,
        gap_override_check: CustomEqualityCheckFn | None = None,
        gap_override_test: CustomTestFn | None = None,
    ) -> partial[TestParam]:
        return partial(
            cls,
            gap_override_check=gap_override_check,
            gap_override_test=gap_override_test,
        )


test_case = TestParam
param = TestParam


class TestParamBundle:
    params: ClassVar[partial[TestParamBundle]]
    zip: ClassVar[partial[TestParamBundle]]
    product: ClassVar[partial[TestParamBundle]]
    singular_params: ClassVar[partial[TestParamBundle]]

    @overload
    def __init__[
        T: Problem[ProbInputType, ProbOutputType]
    ](
        self,
        *args: Any,
        gap_expect: Any | None = None,
        gap_expect_stdout: str | Sequence[str] | None = None,
        gap_hidden: bool = False,
        gap_name: str | None = None,
        gap_extra_credit: float | None = None,
        gap_override_check: CustomEqualityCheckFn | None = None,
        gap_override_test: CustomTestFn | None = None,
        gap_description: str | None = None,
        gap_is_pipeline: bool = False,
        gap_score: float | None = None,
        gap_product: bool = False,
        gap_zip: bool = False,
        gap_params: bool = True,
        gap_singular_params: bool = False,
        **kwargs,
    ) -> None:
        ...

    @overload
    def __init__[
        T: Problem[ProbInputType, ProbOutputType]
    ](
        self,
        *args: Any,
        gap_expect: Any | None = None,
        gap_expect_stdout: str | Sequence[str] | None = None,
        gap_hidden: bool = False,
        gap_name: str | None = None,
        gap_extra_credit: float | None = None,
        gap_override_check: CustomEqualityCheckFn | None = None,
        gap_override_test: CustomTestFn | None = None,
        gap_description: str | None = None,
        gap_is_pipeline: bool = False,
        gap_weight: float | None = None,
        gap_product: bool = False,
        gap_zip: bool = False,
        gap_params: bool = True,
        gap_singular_params: bool = False,
        **kwargs: Any,
    ) -> None:
        ...

    def __init__(
        self,
        *args: Iterable[Any] | Any,
        gap_product: bool = False,
        gap_zip: bool = False,
        gap_params: bool = True,
        gap_singular_params: bool = False,
        **kwargs: Any,
    ) -> None:
        if (gap_params + gap_zip + gap_product + gap_singular_params) != 1:
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

        # pop aga keywords out
        gap_kwargs_dict = {
            kwd.value: kwargs.pop(kwd.value)
            for kwd in GapReservedKeywords
            if kwd.value in kwargs
        }

        if gap_params:
            # build final params
            # So we're allowing [param(1, 2), [3, 4]] as a valid input
            self.final_params: List[TestParam] = type(self).parse_params(
                *args, **kwargs
            )
        elif gap_singular_params:
            self.final_params = type(self).parse_singular_params(*args, **kwargs)
        elif gap_zip or gap_product:
            self.final_params = type(self).parse_zip_or_product(
                *args, gap_zip=gap_zip, gap_product=gap_product, **kwargs
            )
        else:
            raise InternalError("TestParamBundle.__init__ should not reach here.")

        type(self).add_gap_kwargs(gap_kwargs_dict, self.final_params)

    @staticmethod
    def parse_params(*args: Iterable[Any], **kwargs: Any) -> List[TestParam]:
        """Parse the parameters for param sequence."""
        if kwargs:
            raise ValueError("gap_params=True ignores non-aga kwargs")

        return list(arg if isinstance(arg, TestParam) else param(*arg) for arg in args)

    @staticmethod
    def parse_singular_params(*args: Iterable[Any], **kwargs: Any) -> List[TestParam]:
        """Parse the parameters for param sequence."""
        if kwargs:
            raise ValueError("gap_singular_params=True ignores non-aga kwargs")

        return list(arg if isinstance(arg, TestParam) else param(arg) for arg in args)

    @staticmethod
    def parse_zip_or_product(
        *args: Iterable[Any],
        gap_product: bool = False,
        gap_zip: bool = False,
        **kwargs: Any,
    ) -> List[TestParam]:
        """Parse parameters for zip or product."""
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
        # process aga input type
        for gap_kwarg_key, gap_kwarg_value in gap_kwargs.items():
            if isinstance(gap_kwarg_value, Iterable) and not isinstance(
                gap_kwarg_value, str
            ):
                gap_kwargs[gap_kwarg_key] = list(gap_kwarg_value)
            else:
                gap_kwargs[gap_kwarg_key] = [gap_kwarg_value] * len(final_params)

        # validate aga input type
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

        # the aga kwargs list we want
        gap_kwargs_list: List[Dict[str, Any]] = [
            dict(zip(gap_kwargs.keys(), gap_kwarg_value))
            for gap_kwarg_value in zip(*gap_kwargs.values())
        ]

        if not gap_kwargs_list:
            # generate default aga kwargs dict if there are no aga kwargs
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

    @classmethod
    def bind_override(
        cls,
        *,
        gap_override_check: CustomEqualityCheckFn | None = None,
        gap_override_test: CustomTestFn | None = None,
    ) -> partial[TestParamBundle]:
        return partial(
            cls,
            gap_override_check=gap_override_check,
            gap_override_test=gap_override_test,
        )


test_cases = TestParamBundle
test_cases_params = partial(test_cases, aga_params=True)
test_cases_zip = partial(test_cases, aga_zip=True)
test_cases_product = partial(test_cases, aga_product=True)
test_cases_singular_params = partial(test_cases, aga_singular_params=True)
test_cases.params = test_cases_params
test_cases.product = test_cases_product
test_cases.zip = test_cases_zip
test_cases.singular_params = test_cases_singular_params
