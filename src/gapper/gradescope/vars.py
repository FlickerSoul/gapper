"""The default variable definitions for the Gradescope autograder."""
from pathlib import Path

DEFAULT_TESTER_PICKLE_NAME = "tester.pckl"

AUTOGRADER_ROOT = Path("/autograder")
AUTOGRADER_SRC = AUTOGRADER_ROOT / "source"
AUTOGRADER_SUBMISSION = AUTOGRADER_ROOT / "submission"
AUTOGRADER_METADATA = AUTOGRADER_ROOT / "submission_metadata.json"
AUTOGRADER_OUTPUT = AUTOGRADER_ROOT / "results/results.json"
AUTOGRADER_TESTER_PICKLE = AUTOGRADER_SRC / DEFAULT_TESTER_PICKLE_NAME
