from __future__ import annotations

from pathlib import Path

__all__ = ["run_autograder"]

from gapper.core.tester import Tester
from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata
from gapper.gradescope.datatypes.gradescope_output import GradescopeJson

AUTOGRADER_ROOT = Path("/autograder")
AUTOGRADER_SRC = AUTOGRADER_ROOT / "source"
AUTOGRADER_SUBMISSION = AUTOGRADER_ROOT / "submission"
AUTOGRADER_METADATA = AUTOGRADER_ROOT / "submission_metadata.json"
AUTOGRADER_OUTPUT = AUTOGRADER_ROOT / "results/results.json"
AUTOGRADER_TESTER_PICKLE = AUTOGRADER_SRC / "tester.pckl"


def run_autograder(
    tester_path: Path = AUTOGRADER_TESTER_PICKLE,
    submission_dir: Path = AUTOGRADER_SUBMISSION,
    metadata_file: Path = AUTOGRADER_METADATA,
    output_file: Path = AUTOGRADER_OUTPUT,
) -> None:
    tester: Tester = Tester.from_file(tester_path)
    tester.load_submission_from_path(submission_dir)
    metadata = GradescopeSubmissionMetadata.from_file(metadata_file)
    results = tester.load_submission_from_path(submission_dir).run(metadata=metadata)
    GradescopeJson.from_test_results(results, metadata, save_path=output_file)
