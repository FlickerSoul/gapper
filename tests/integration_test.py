import subprocess
from itertools import product
from pathlib import Path
from typing import Tuple

import pytest

from tests.conftest import preset_problem_paths, preset_submission_paths


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
        "python",
        "-m",
        "gapper",
        "run",
        str(prob.absolute()),
        str(sub.absolute()),
    ]

    if verbose:
        args.append("-v")

    subprocess.run(args, check=True)


@pytest.mark.parametrize(
    "prob, verbose",
    product(
        sorted(preset_problem_paths(), key=lambda x: x.name),
        [True, False],
    ),
)
def test_problem_check(prob: Path, verbose: bool) -> None:
    args = [
        "python",
        "-m",
        "gapper",
        "check",
        str(prob.absolute()),
    ]

    if verbose:
        args.append("-v")

    subprocess.run(args, check=True)


@pytest.mark.parametrize(
    "prob, verbose",
    product(
        sorted(preset_problem_paths(), key=lambda x: x.name),
        [True, False],
    ),
)
def test_problem_gen(prob: Path, verbose: bool, tmp_path: Path) -> None:
    args = [
        "python",
        "-m",
        "gapper",
        "gen",
        str(prob.absolute()),
        "-s",
        str(tmp_path.absolute()),
        "-y",
    ]

    if verbose:
        args.append("-v")

    subprocess.run(args, check=True)
