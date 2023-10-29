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
    @test_cases.params([1], [2], [3])
    @problem()
    def square(a: int) -> int:
        return a**2

    assert len(square.test_cases) == 3


def test_test_params_param_iter() -> None:
    @test_cases.param_iter([i] for i in range(3))
    @problem()
    def square(a: int) -> int:
        return a**2

    assert len(square.test_cases) == 3
