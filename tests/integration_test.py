import sys
from itertools import product
from pathlib import Path
from typing import Tuple

import pytest
from typer.testing import CliRunner

from gapper.cli import app as cli_app
from tests.conftest import preset_problem_paths, preset_submission_paths


@pytest.fixture(autouse=True)
def injection_clean_up() -> None:
    try:
        import gapper.injection  # type: ignore
    except ImportError:
        pass
    else:
        del sys.modules["gapper.injection"]
        del gapper.injection  # type: ignore


@pytest.mark.parametrize(
    "prob_sub, verbose",
    product(
        zip(
            sorted(preset_problem_paths(), key=lambda x: x.name),
            sorted(preset_submission_paths(), key=lambda x: x.name),
        ),
        [True, False],
    ),
)
def test_problem_run(prob_sub: Tuple[Path, Path], verbose: bool) -> None:
    prob, sub = prob_sub
    assert prob.name == sub.name
    args = [
        "run",
        str(prob.absolute()),
        str(sub.absolute()),
    ]

    if verbose:
        args.append("-v")

    result = CliRunner().invoke(cli_app, args)
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "prob, verbose",
    product(
        sorted(preset_problem_paths(), key=lambda x: x.name),
        [True, False],
    ),
)
def test_problem_check(prob: Path, verbose: bool) -> None:
    args = [
        "check",
        str(prob.absolute()),
    ]

    if verbose:
        args.append("-v")

    result = CliRunner().invoke(cli_app, args)
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "prob, verbose",
    product(
        sorted(preset_problem_paths(), key=lambda x: x.name),
        [True, False],
    ),
)
def test_problem_gen(prob: Path, verbose: bool, tmp_path: Path) -> None:
    args = [
        "gen",
        str(prob.absolute()),
        "-s",
        str(tmp_path.absolute()),
        "-y",
    ]

    if verbose:
        args.append("-v")

    result = CliRunner().invoke(cli_app, args)
    file_paths = [*tmp_path.glob("*.zip")]

    assert result.exit_code == 0
    assert len(file_paths) == 1


@pytest.mark.parametrize(
    "prob, verbose",
    product(
        sorted(preset_problem_paths(), key=lambda x: x.name),
        [True, False],
    ),
)
def test_problem_gen_with_file_path(prob: Path, verbose: bool, tmp_path: Path) -> None:
    file_path = tmp_path / "test.zip"

    args = [
        "gen",
        str(prob.absolute()),
        "-s",
        str(file_path.absolute()),
        "-y",
    ]

    if verbose:
        args.append("-v")

    result = CliRunner().invoke(cli_app, args)

    assert result.exit_code == 0
    assert file_path.exists()
