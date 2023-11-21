import random
import tempfile
from pathlib import Path

from gapper import pre_test, problem, tcs
from gapper.core.test_result import TestResult
from gapper.gradescope.datatypes.gradescope_meta import GradescopeSubmissionMetadata

files = []


def make_files(file_num: int) -> None:
    for _ in range(file_num):
        with tempfile.TemporaryDirectory(delete=False) as directory:
            file_name = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=5))
            path = Path(directory) / file_name
            files.append(path)
            with open(files[-1], "w") as f:
                for _ in range(random.randint(1, 100)):
                    f.write(f"{random.randint(1, 100)}\n")


def file_generator(
    result_proxy: TestResult | None, metadata: GradescopeSubmissionMetadata | None
) -> None:
    make_files(5)


@tcs.singular_param_iter(files)
@pre_test(file_generator, as_test_case=False)
@problem()
def get_file_lines(file_name: str) -> int:
    with open(file_name) as f:
        return len(f.readlines())


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": (),
    "easy_context": True,
    "extras": {},
}
