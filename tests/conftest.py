import importlib.util
import sys
from pathlib import Path
from typing import Any, Generator, List

import pytest

from gapper.core.problem import Problem, ProblemConfig
from gapper.core.tester import Tester

TEST_ASSET_FOLDER = Path(__file__).parent / "assets"

TEST_PROBLEM_FOLDER = TEST_ASSET_FOLDER / "problems"
NO_PROBLEM_FILE_FOLDER = TEST_ASSET_FOLDER / "no_problem_defined"
SINGLE_PROBLEM_DEFINED_FOLDER = TEST_ASSET_FOLDER / "single_problem_defined"
INJECTION_PROBLEM_FOLDER = TEST_ASSET_FOLDER / "injection_problems"

TEST_SUBMISSIONS_FOLDER = TEST_ASSET_FOLDER / "submissions"
NO_SUBMISSION_FOLDER = TEST_ASSET_FOLDER / "no_submission_defined"
SINGLE_SUBMISSION_FOLDER = TEST_ASSET_FOLDER / "single_submission_defined"
MULTIPLE_SUBMISSIONS_FOLDER = TEST_ASSET_FOLDER / "multiple_submissions_defined"

PROBLEM_CONFIG_VAR_NAME = "__problem_config__"


def make_problem_name(name: str) -> str:
    return f"preset_problem_{name}"


def make_tester_name(name: str) -> str:
    return f"preset_tester_for_problem_{name}"


def _get_problem_config(problem_path: Path) -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location("module", problem_path)

    if spec is None:
        raise ValueError(f"Problem file {problem_path} is not a valid python file.")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, PROBLEM_CONFIG_VAR_NAME)


def generate_problem_fixtures(problem_path: Path) -> None:
    problem_name = make_problem_name(problem_path.name)
    tester_name = make_tester_name(problem_path.name)

    @pytest.fixture(scope="session", name=problem_name)
    def _problem_wrapper() -> Problem[Any, Any]:
        config = _get_problem_config(problem_path)
        problem = Problem.from_path(problem_path)
        setattr(problem, PROBLEM_CONFIG_VAR_NAME, config)
        return problem

    @pytest.fixture(scope="session", name=tester_name)
    def _tester_wrapper(request: pytest.FixtureRequest) -> Tester[Any, Any]:
        problem: Problem[Any, Any] = Problem.from_path(problem_path)
        return Tester(problem=problem)

    setattr(sys.modules[__name__], problem_name, _problem_wrapper)
    setattr(sys.modules[__name__], tester_name, _tester_wrapper)


def preset_problem_paths() -> Generator[Path, None, None]:
    for prob_path in TEST_PROBLEM_FOLDER.iterdir():
        if prob_path.is_file() and prob_path.suffix == ".py":
            yield prob_path


for _prob_path in preset_problem_paths():
    generate_problem_fixtures(_prob_path)


def preset_submission_paths() -> Generator[Path, None, None]:
    for sub_path in TEST_SUBMISSIONS_FOLDER.iterdir():
        if sub_path.is_file() and sub_path.suffix == ".py":
            yield sub_path


@pytest.fixture()
def problem_fixture(request: pytest.FixtureRequest) -> Problem[Any, Any]:
    partial_prob_name: Path = request.param
    return request.getfixturevalue(make_problem_name(partial_prob_name.name))


@pytest.fixture()
def tester_fixture(request: pytest.FixtureRequest) -> Problem[Any, Any]:
    partial_prob_name: Path = request.param
    return request.getfixturevalue(make_tester_name(partial_prob_name.name))


@pytest.fixture()
def all_preset_problems(request) -> List[Problem[Any, Any]]:
    return [
        request.getfixturevalue(make_problem_name(prob_name.name))
        for prob_name in preset_problem_paths()
    ]


@pytest.fixture()
def all_preset_problem_tester_with_default_config(
    all_preset_problems,
) -> List[Tester[Any, Any]]:
    return [Tester(problem=problem) for problem in all_preset_problems]


@pytest.fixture()
def dummy_problem() -> Problem[Any, Any]:
    return Problem(lambda: None, config=ProblemConfig())


@pytest.fixture(autouse=True)
def injection_clean_up() -> None:
    try:
        import gapper.injection  # type: ignore
    except ImportError:
        pass
    else:
        del sys.modules["gapper.injection"]
        del gapper.injection  # type: ignore
