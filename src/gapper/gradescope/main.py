from __future__ import annotations

from pathlib import Path

__all__ = ["run_autograder"]

from gapper.core.tester import Tester
from gapper.gradescope.datatypes.gradescope_meta import \
    GradescopeSubmissionMetadata
from gapper.gradescope.datatypes.gradescope_output import GradescopeJson
from gapper.gradescope.vars import (AUTOGRADER_METADATA, AUTOGRADER_OUTPUT,
                                    AUTOGRADER_SUBMISSION,
                                    AUTOGRADER_TESTER_PICKLE)


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
