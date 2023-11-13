from itertools import chain, product
from typing import Any

import pytest
from gapper.core.errors import InternalError
from gapper.core.test_result import TestResult


@pytest.mark.parametrize(
    "instance_prop, value",
    [
        pytest.param(*args, id=", ".join(map(str, args)))
        for args in chain(
            product(["name"], ["test name"]),
            product(["score"], [1, 2.0, 3.0]),
            product(["max_score"], [1, 2.0, 3.0]),
            product(["weight"], [1, 2, 3]),
            product(["extra_points"], [1, 2.0, 3.0]),
            product(["pass_status"], ["passed", "failed"]),
            product(["hidden"], [True, False]),
        )
    ],
)
def test_test_result_setters(instance_prop: str, value: Any):
    result = TestResult("test")
    getattr(result, f"set_{instance_prop}")(value)
    assert getattr(result, instance_prop) == value


def test_test_result_descriptions() -> None:
    result = TestResult("test")
    result.add_description("test description")
    assert result.descriptions == ["test description"]
    result.set_descriptions(["test description 1", "test description 2"])
    assert result.descriptions == ["test description 1", "test description 2"]


def test_add_errors() -> None:
    result = TestResult("test")
    first_error = InternalError("test error")
    second_error = InternalError("test error 2")

    result.add_error(first_error, set_failed=False)
    assert result.errors == [first_error]
    assert result.pass_status is None

    result.add_error(second_error, set_failed=True)
    assert result.errors == [first_error, second_error]
    assert result.pass_status == "failed"


def test_test_result_rich_name() -> None:
    default_name = "default_name"
    result = TestResult(default_name)
    assert result.rich_test_name == default_name
    custom_name = "test_name"
    result.set_name(custom_name)
    assert result.rich_test_name == f"{custom_name} {default_name}"


def test_test_result_rich_output() -> None:
    result = TestResult("test")
    result.set_pass_status("passed")
    assert result.rich_test_output == "Passed"

    result.add_description("test description")
    assert result.rich_test_output == ("Passed\n" + "Description(s): \n" + "  test description")

    result.add_error(InternalError("test error"), set_failed=False)
    assert (
        result.rich_test_output == "Passed\n"
        "Description(s): \n"
        "  test description\n"
        "Error(s): \n"
        "  Internal Error. Please report this to the developers. \n"
        "  The reason is following: \n"
        "    test error\n"
        "  Stack Trace: \n"
        "    Not Provided\n"
    )

    result.set_descriptions([])
    assert result.rich_test_output == (
        "Passed\n"
        "Error(s): \n"
        "  Internal Error. Please report this to the developers. \n"
        "  The reason is following: \n"
        "    test error\n"
        "  Stack Trace: \n"
        "    Not Provided\n"
    )

    result.add_error(InternalError("test error 2"), set_failed=True)
    assert result.rich_test_output == (
        "Failed\n"
        "Error(s): \n"
        "  Internal Error. Please report this to the developers. \n"
        "  The reason is following: \n"
        "    test error\n"
        "  Stack Trace: \n"
        "    Not Provided\n"
        "\n"
        "  Internal Error. Please report this to the developers. \n"
        "  The reason is following: \n"
        "    test error 2\n"
        "  Stack Trace: \n"
        "    Not Provided\n"
    )
