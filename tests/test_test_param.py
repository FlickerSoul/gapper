import pytest

from gapper import problem, test_cases


def test_test_params_gap_kwargs_length_matching() -> None:
    with pytest.raises(ValueError):

        @test_cases.params([1], [2], [3], gap_hidden=[True, False])
        @problem()
        def square(a: int) -> int:
            return a**2

    with pytest.raises(ValueError):

        @test_cases.params(
            [1], [2], [3], gap_hidden=[True, False, False], gap_max_score=[1, 2]
        )
        @problem()
        def square(a: int) -> int:
            return a**2


def test_test_params_params() -> None:
    bundle = test_cases.params([1], [2], [3])

    assert len(bundle.final_params) == 3


def test_test_params_param_iter() -> None:
    bundle = test_cases.param_iter([i] for i in range(3))

    assert len(bundle.final_params) == 3


def test_test_singular_params() -> None:
    # singular params is expected not to unfold
    bundle = test_cases.singular_params(
        [i for i in range(3)],
        [i for i in range(3)],
    )

    assert len(bundle.final_params) == 2


def test_test_singular_param_iter() -> None:
    # singular params is expected not to unfold
    bundle = test_cases.singular_param_iter([i for i in range(3)] for _ in range(10))

    assert len(bundle.final_params) == 10
