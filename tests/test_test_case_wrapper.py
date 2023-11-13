from unittest.mock import patch

import pytest
from gapper.core.problem import Problem
from gapper.core.test_parameter import TestParam
from gapper.core.test_result import TestResult
from gapper.core.unittest_wrapper import TestCaseWrapper

from tests.conftest import make_problem_name


@pytest.mark.parametrize(
    "test_param",
    (
        pytest.param(p, id=p.format(with_gap_kwargs=True))
        for p in [
            TestParam(gap_name="custom_test", gap_weight=2),
            TestParam(gap_name="custom_test", gap_weight=2, gap_hidden=True),
            TestParam(gap_name="custom_test", gap_weight=2, gap_extra_points=1),
            TestParam(gap_name="custom_test", gap_max_score=1),
            TestParam(
                gap_name="custom_test",
                gap_max_score=1,
                gap_description="test description",
                gap_hidden=True,
            ),
            TestParam(
                gap_name="custom_test",
                gap_max_score=1,
                gap_description=["test description 1", "test description 2"],
            ),
        ]
    ),
)
def test_result_init(dummy_problem, test_param: TestParam) -> None:
    test_result = TestResult("test")

    with patch(
        "gapper.core.unittest_wrapper.TestCaseWrapper._run_test",
        new=lambda _, y: y,
    ):
        wrapper = TestCaseWrapper(test_param, dummy_problem)
        wrapper.run_test(None, test_result)

    for param_attr, result_attr in [
        ("gap_name", "name"),
        ("gap_max_score", "max_score"),
        ("gap_weight", "weight"),
        ("gap_extra_points", "extra_points"),
        ("gap_hidden", "hidden"),
    ]:
        assert getattr(test_param.param_info, param_attr) == getattr(
            test_result, result_attr
        )

    des = getattr(test_param.param_info, "gap_description")
    if isinstance(des, str):
        des = [des]
    elif des is None:
        des = []
    assert test_result.descriptions == des


def test_gap_check(request: pytest.FixtureRequest) -> None:
    gap_check_tester: Problem = request.getfixturevalue(
        make_problem_name("sanity_check_with_gap_expect.py")
    )

    for test in gap_check_tester.generate_tests():
        passed, result, out = test.check_test()
        assert passed
