import importlib.util
import sys
from pathlib import Path
from typing import Any, List, Generator

import pytest

from gap.core.problem import Problem
from gap.core.tester import Tester

TEST_ASSET_FOLDER = Path(__file__).parent / "assets"
TEST_PROBLEM_FOLDER = TEST_ASSET_FOLDER / "problems"
TEST_SUBMISSIONS_FOLDER = TEST_ASSET_FOLDER / "submissions"

PROBLEM_CONFIG_VAR_NAME = "__problem_config__"


def _make_problem_name(name: str) -> str:
    return f"preset_problem_{name}"


def _make_tester_name(name: str) -> str:
    return f"preset_tester_for_problem_{name}"


def _get_problem_config(problem_path: Path) -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location("module", problem_path)

    if spec is None:
        raise ValueError(f"Problem file {problem_path} is not a valid python file.")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, PROBLEM_CONFIG_VAR_NAME)


def generate_problem_fixtures(problem_path: Path) -> None:
    problem_name = _make_problem_name(problem_path.name)
    tester_name = _make_tester_name(problem_path.name)

    @pytest.fixture(scope="session", name=problem_name)
    def _problem_wrapper() -> Problem[Any, Any]:
        config = _get_problem_config(problem_path)
        problem = Problem.from_file(problem_path)
        setattr(problem, PROBLEM_CONFIG_VAR_NAME, config)
        return problem

    @pytest.fixture(scope="session", name=tester_name)
    def _tester_wrapper(request: pytest.FixtureRequest) -> Tester[Any, Any]:
        problem: Problem[Any, Any] = Problem.from_file(problem_path)
        return Tester(problem=problem)

    setattr(sys.modules[__name__], problem_name, _problem_wrapper)
    setattr(sys.modules[__name__], tester_name, _tester_wrapper)


def preset_problem_paths() -> Generator[Path, None, None]:
    for prob_path in TEST_PROBLEM_FOLDER.iterdir():
        if prob_path.is_file() and prob_path.suffix == ".py":
            yield prob_path


for _prob_path in preset_problem_paths():
    generate_problem_fixtures(_prob_path)


@pytest.fixture()
def problem_fixture(request: pytest.FixtureRequest) -> Problem[Any, Any]:
    partial_prob_name: Path = request.param
    return request.getfixturevalue(_make_problem_name(partial_prob_name.name))


@pytest.fixture()
def tester_fixture(request: pytest.FixtureRequest) -> Problem[Any, Any]:
    partial_prob_name: Path = request.param
    return request.getfixturevalue(_make_tester_name(partial_prob_name.name))


@pytest.fixture()
def all_preset_problems(request) -> List[Problem[Any, Any]]:
    return [
        request.getfixturevalue(_make_problem_name(prob_name.name))
        for prob_name in preset_problem_paths()
    ]


@pytest.fixture()
def all_preset_problem_tester_with_default_config(
    all_preset_problems,
) -> List[Tester[Any, Any]]:
    return [Tester(problem=problem) for problem in all_preset_problems]
