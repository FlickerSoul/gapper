import random
import tempfile
from pathlib import Path
from typing import Generator

from gapper import pre_tests, problem, tcs
from gapper.core.types import PreTestsData

files = []


def make_files(file_num: int) -> Generator[None, None, None]:
    with tempfile.TemporaryDirectory() as directory:
        for _ in range(file_num):
            file_name = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=5))
            path = Path(directory) / file_name
            files.append(path)
            with open(files[-1], "w") as f:
                for _ in range(random.randint(1, 100)):
                    f.write(f"{random.randint(1, 100)}\n")

        yield


def file_generator(_: PreTestsData) -> Generator[None, None, None]:
    return make_files(5)


@tcs.singular_param_iter(files)
@pre_tests(file_generator, as_test_case=False)
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
