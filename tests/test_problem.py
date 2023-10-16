from typing import Any

import pytest

from gap import problem
from gap.core.problem import Problem
from gap.core.test_parameter import TestParam
from gap.core.unittest_wrapper import TestCaseWrapper
from tests.conftest import (
    TEST_PROBLEM_FOLDER,
    PROBLEM_CONFIG_VAR_NAME,
    preset_problem_paths,
)


def test_problem_is_script() -> None:
    @problem(is_script=True)
    def prob():
        pass

    assert prob.config.is_script
    assert prob.config.check_stdout
    assert prob.config.mock_input


def test_problem_is_script_flag_conflict() -> None:
    with pytest.raises(ValueError):

        @problem(is_script=True, check_stdout=True)
        def prob():
            pass

    with pytest.raises(ValueError):

        @problem(is_script=True, mock_input=True)
        def prob():
            pass

    with pytest.raises(ValueError):

        @problem(is_script=True, check_stdout=True, mock_input=True)
        def prob():
            pass


def test_problem_std_flags() -> None:
    @problem(check_stdout=True)
    def prob():
        pass

    assert not prob.config.is_script
    assert prob.config.check_stdout
    assert not prob.config.mock_input

    @problem(mock_input=True)
    def prob():
        pass

    assert not prob.config.is_script
    assert not prob.config.check_stdout
    assert prob.config.mock_input

    @problem(check_stdout=True, mock_input=True)
    def prob():
        pass

    assert not prob.config.is_script
    assert prob.config.check_stdout
    assert prob.config.mock_input


def test_capture_list() -> None:
    @problem(context=["a", "b"])
    def prob():
        pass

    assert prob.config.captured_context == ["a", "b"]


@pytest.mark.parametrize(
    "problem_fixture",
    [pytest.param(p, id=p.name) for p in preset_problem_paths()],
    indirect=True,
)
def test_load_problem(problem_fixture: Problem[Any, Any]) -> None:
    config = getattr(problem_fixture, PROBLEM_CONFIG_VAR_NAME)
    for key, desired_value in config.items():
        actual_value = getattr(problem_fixture.config, key)
        assert actual_value == desired_value, (
            f"The config of {key} is of the problem does not match the desired. "
            f"{desired_value} != {actual_value}"
        )


@pytest.mark.parametrize(
    "problem_fixture",
    [pytest.param(p, id=p.name) for p in preset_problem_paths()],
    indirect=True,
)
def test_generate_test_cases(problem_fixture: Problem[Any, Any]) -> None:
    for test_case, test_param in zip(
        problem_fixture.generate_tests(), problem_fixture.test_cases
    ):  # type: TestCaseWrapper, TestParam
        assert test_case.problem == problem_fixture
        assert test_case.test_param == test_param
        assert test_case.metadata is None
        assert test_case.context is None
