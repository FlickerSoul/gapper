"""The main module for the Gradescope autograder."""
from __future__ import annotations

from pathlib import Path

__all__ = ["run_autograder"]

from gapper.core.result_synthesizer import ResultSynthesizer
from gapper.core.tester import Tester
from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata
from gapper.gradescope.vars import (
    AUTOGRADER_METADATA,
    AUTOGRADER_OUTPUT,
    AUTOGRADER_SUBMISSION,
    AUTOGRADER_TESTER_PICKLE,
)


def run_autograder(
    tester_path: Path = AUTOGRADER_TESTER_PICKLE,
    submission_dir: Path = AUTOGRADER_SUBMISSION,
    metadata_file: Path = AUTOGRADER_METADATA,
    output_file: Path = AUTOGRADER_OUTPUT,
) -> None:
    """Run the autograder.

    :param tester_path: The path to the tester pickle file.
    :param submission_dir: The path to the submission directory.
    :param metadata_file: The path to the metadata file.
    :param output_file: The path to the output file.
    """
    tester: Tester = Tester.from_file(tester_path)
    tester.load_submission_from_path(submission_dir)
    metadata = GradescopeSubmissionMetadata.from_file(metadata_file)
    results = tester.load_submission_from_path(submission_dir).run(metadata=metadata)
    ResultSynthesizer(
        results=results, post_tests=tester.problem.post_tests, metadata=metadata
    ).to_gradescope_json(save_path=output_file)
