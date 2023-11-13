from typing import Any, Tuple

import pytest
from gapper import problem
from gapper.core.errors import MultipleProblemsDefinedError, NoProblemDefinedError
from gapper.core.injection import InjectionHandler
from gapper.core.problem import Problem
from gapper.core.problem.extras.gradescope_connect import GSConnectConfig, build_connect_config

from tests.conftest import (
    INJECTION_PROBLEM_FOLDER,
    NO_PROBLEM_FILE_FOLDER,
    PROBLEM_CONFIG_VAR_NAME,
    SINGLE_PROBLEM_DEFINED_FOLDER,
    TEST_PROBLEM_FOLDER,
    preset_problem_paths,
)


def test_problem_is_script() -> None:
    @problem(is_script=True)
    def prob():
        """Test problem is_script flag"""

    assert prob.config.is_script
    assert prob.config.check_stdout
    assert prob.config.mock_input


def test_problem_is_script_flag_conflict() -> None:
    with pytest.raises(ValueError):

        @problem(is_script=True, check_stdout=True)
        def prob():
            """Test problem is_script flag conflict"""

    with pytest.raises(ValueError):

        @problem(is_script=True, mock_input=True)
        def prob():
            """Test problem is_script flag conflict"""

    with pytest.raises(ValueError):

        @problem(is_script=True, check_stdout=True, mock_input=True)
        def prob():
            """Test problem is_script flag conflict"""


def test_problem_std_flags() -> None:
    @problem(check_stdout=True)
    def prob():
        """Test problem std flags"""

    assert not prob.config.is_script
    assert prob.config.check_stdout
    assert not prob.config.mock_input

    @problem(mock_input=True)
    def prob():
        """Test problem std flags"""

    assert not prob.config.is_script
    assert not prob.config.check_stdout
    assert prob.config.mock_input

    @problem(check_stdout=True, mock_input=True)
    def prob():
        """Test problem std flags"""

    assert not prob.config.is_script
    assert prob.config.check_stdout
    assert prob.config.mock_input


def test_capture_list() -> None:
    @problem(context=["a", "b"])
    def prob():
        """Test problem capture context"""

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
            f"The config of {key} is of the problem does not match the desired. " f"{desired_value} != {actual_value}"
        )


@pytest.mark.parametrize(
    "problem_fixture",
    [pytest.param(p, id=p.name) for p in preset_problem_paths()],
    indirect=True,
)
def test_generate_test_cases(problem_fixture: Problem[Any, Any]) -> None:
    for test_case, test_param in zip(problem_fixture.generate_tests(), problem_fixture.test_cases):  # type: TestCaseWrapper, TestParam
        assert test_case.problem == problem_fixture
        assert test_case.test_param == test_param
        assert test_case.metadata is None
        assert test_case.context is None


def test_no_problem_loading_error() -> None:
    with pytest.raises(NoProblemDefinedError):
        Problem.from_path(NO_PROBLEM_FILE_FOLDER)


def test_load_problem_from_folder() -> None:
    Problem.from_path(SINGLE_PROBLEM_DEFINED_FOLDER)


def test_multiple_problem_loading_error() -> None:
    with pytest.raises(MultipleProblemsDefinedError):
        Problem.from_path(TEST_PROBLEM_FOLDER)


def test_load_auto_inject() -> None:
    injection_handle = InjectionHandler().setup(
        INJECTION_PROBLEM_FOLDER,
        [INJECTION_PROBLEM_FOLDER / "temp_injected_content.py"],
    )
    injection_handle.inject()
    Problem.from_path(INJECTION_PROBLEM_FOLDER / "auto_inject.py")


@pytest.mark.parametrize(
    "inputs, expected",
    [
        [("112358", "2468"), GSConnectConfig("112358", "2468")],
        [("112358", None), None],
        [
            (
                "https://www.gradescope.com/courses/112358/assignments/2468/review_grades",
                None,
            ),
            GSConnectConfig("112358", "2468"),
        ],
        [
            ("https://www.gradescope.com/courses/112358/assignments/2468/", None),
            GSConnectConfig("112358", "2468"),
        ],
        [
            ("https://www.gradescope.com/courses/112358/assignments/2468", None),
            GSConnectConfig("112358", "2468"),
        ],
        [
            ("www.gradescope.com/courses/112358/assignments/2468/review_grades", None),
            GSConnectConfig("112358", "2468"),
        ],
        [
            ("gradescope.com/courses/112358/assignments/2468/review_grades", None),
            GSConnectConfig("112358", "2468"),
        ],
        [
            (
                "https://www.gradescope.com/courses/112358/assignments/2468/review_grades",
                "112358",
            ),
            None,
        ],
    ],
)
def test_build_connect_config(inputs: Tuple[str, str | None], expected: GSConnectConfig | None) -> None:
    if expected:
        assert build_connect_config(*inputs) == expected
    else:
        with pytest.raises(ValueError):
            build_connect_config(*inputs)
