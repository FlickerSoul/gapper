"""The main module for the Gradescope autograder."""
from __future__ import annotations

import logging
from pathlib import Path

__all__ = ["run_autograder"]

from gapper.core.errors import InternalError, StudentError
from gapper.core.result_synthesizer import ResultSynthesizer
from gapper.core.tester import Tester
from gapper.gradescope.datatypes.gradescope_meta import (
    GradescopeSubmissionMetadata,
)
from gapper.gradescope.datatypes.gradescope_output import GradescopeJson
from gapper.gradescope.vars import (
    AUTOGRADER_METADATA,
    AUTOGRADER_OUTPUT,
    AUTOGRADER_SUBMISSION,
    AUTOGRADER_TESTER_PICKLE,
)

_autograder_main_logger = logging.getLogger("gapper.gradescope.main")


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
    error: StudentError | InternalError | None = None

    try:
        tester: Tester = Tester.from_file(tester_path)
        tester.load_submission_from_path(submission_dir)
        metadata = GradescopeSubmissionMetadata.from_file(metadata_file)
        results = tester.run(metadata=metadata)
        ResultSynthesizer(results=results, metadata=metadata).to_gradescope_json(
            save_path=output_file
        )
    except InternalError as e:
        _autograder_main_logger.error(
            f"Internal error happened during execution: {e.format()}"
        )
        error = e
    except StudentError as e:
        _autograder_main_logger.error(
            f"Student error happened during execution: {e.format()}"
        )
        error = e
    except Exception as e:
        _autograder_main_logger.error(f"Unknown error occurred: {e}.")
        error = InternalError(e)

    if error is not None:
        GradescopeJson.from_error(error, save_path=output_file)
