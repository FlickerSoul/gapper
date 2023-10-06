from __future__ import annotations

from pathlib import Path

__all__ = ["run_autograder"]

from gap.core.tester import Tester
from gap.loaders.packed_tester_loaders import load_packed_tester

AUTOGRADER_ROOT = Path("/autograder")
AUTOGRADER_SRC = AUTOGRADER_ROOT / "source"
AUTOGRADER_SUBMISSION = AUTOGRADER_ROOT / "submission"
AUTOGRADER_METADATA = AUTOGRADER_ROOT / "submission_metadata.json"
AUTOGRADER_OUTPUT = AUTOGRADER_ROOT / "results/results.json"


def run_autograder(
    autograder_path: Path = AUTOGRADER_SRC,
    submission_dir: Path = AUTOGRADER_SUBMISSION,
    metadata_file: Path = AUTOGRADER_METADATA,
    output_file: Path = AUTOGRADER_OUTPUT,
) -> None:
    tester: Tester = load_packed_tester(autograder_path)
