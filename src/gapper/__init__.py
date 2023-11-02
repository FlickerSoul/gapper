"""The gapper (gap) package."""

from .core.problem import problem
from .core.result_synthesizer import post_test
from .core.test_parameter import (
    param,
    test_case,
    test_cases,
    test_cases_param_iter,
    test_cases_params,
    test_cases_product,
    test_cases_singular_param_iter,
    test_cases_singular_params,
    test_cases_zip,
)

__all__ = [
    "problem",
    "param",
    "test_case",
    "test_cases",
    "test_cases_param_iter",
    "test_cases_params",
    "test_cases_product",
    "test_cases_singular_param_iter",
    "test_cases_singular_params",
    "test_cases_zip",
    "post_test",
]
