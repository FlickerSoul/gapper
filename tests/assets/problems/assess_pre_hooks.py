import random
from tempfile import NamedTemporaryFile

from gapper import problem, tc, tcs
from gapper.core.types import PreHookData

apple: int


def generate_file_content(lines: int) -> str:
    return "\n".join(str(random.randint(0, 100)) for _ in range(lines))


def process_file(data: PreHookData):
    case = data.case

    file_content = case.test_param.args[0]
    with NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(file_content)
        f.close()

    assert isinstance(apple, int)

    # replace the argument with the file name
    case.test_param.args = (f.name,)


file_build_tc = tc.bind(gap_pre_hooks=process_file)
file_build_tcs = tcs.bind(gap_pre_hooks=process_file)


@file_build_tcs.singular_params(generate_file_content(6), generate_file_content(10))
@file_build_tc(generate_file_content(0))
@file_build_tc(generate_file_content(5))
@problem(context=["apple"])
def sum_file(file_name: str) -> int:
    with open(file_name) as f:
        return sum(map(lambda line: int(line.strip()), f.readlines()), 0)


__problem_config__ = {
    "is_script": False,
    "check_stdout": False,
    "mock_input": False,
    "captured_context": ["apple"],
    "easy_context": True,
    "extras": {},
}
