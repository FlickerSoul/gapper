import pytest

from gapper import problem, test_cases


def test_test_params_gap_kwargs_length_matching() -> None:
    with pytest.raises(ValueError):

        @test_cases([1], [2], [3], gap_hidden=[True, False])
        @problem()
        def square(a: int) -> int:
            return a**2

    with pytest.raises(ValueError):

        @test_cases(
            [1], [2], [3], gap_hidden=[True, False, False], gap_max_score=[1, 2]
        )
        @problem()
        def square(a: int) -> int:
            return a**2
