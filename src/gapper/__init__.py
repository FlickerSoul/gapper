"""The gapper (gap) package."""

from .core.problem import gs_connect, problem
from .core.test_parameter import (
    param,
    tc,
    tcs,
    test_case,
    test_cases,
    test_cases_param_iter,
    test_cases_params,
    test_cases_product,
    test_cases_singular_param_iter,
    test_cases_singular_params,
    test_cases_zip,
)
from .core.test_result import TestResult
from .core.tester import post_test, pre_test
from .gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata

__all__ = [
    "gs_connect",
    "problem",
    "param",
    "tc",
    "tcs",
    "test_case",
    "test_cases",
    "test_cases_param_iter",
    "test_cases_params",
    "test_cases_product",
    "test_cases_singular_param_iter",
    "test_cases_singular_params",
    "test_cases_zip",
    "post_test",
    "pre_test",
    "TestResult",
    "GradescopeSubmissionMetadata",
]
