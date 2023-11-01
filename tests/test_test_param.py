from typing import Any, Dict, Sequence

import pytest

from gapper import param, problem, test_cases


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


@pytest.mark.parametrize(
    "args, kwargs, results",
    [
        [([1], [2], [3]), {}, (param(1), param(2), param(3))],
        [
            ([1], [2], [3]),
            {"gap_hidden": True},
            (
                param(1, gap_hidden=True),
                param(2, gap_hidden=True),
                param(3, gap_hidden=True),
            ),
        ],
        [
            ([1], [2], param(3, gap_max_score=10)),
            {"gap_max_score": 5},
            (
                param(1, gap_max_score=5),
                param(2, gap_max_score=5),
                param(3, gap_max_score=5),
            ),
        ],
        [
            ([1], [2], param(3)),
            {"gap_hidden": True},
            (
                param(1, gap_hidden=True),
                param(2, gap_hidden=True),
                param(3, gap_hidden=True),
            ),
        ],
    ],
)
def test_test_params_params(
    args: Sequence[Any], kwargs: Dict, results: Sequence[param]
) -> None:
    bundle = test_cases.params(*args, **kwargs)

    assert len(bundle.final_params) == len(results)
    for i, j in zip(bundle.final_params, results):
        assert i == j


@pytest.mark.parametrize(
    "args, kwargs, results",
    [
        (
            [
                [[i, i] for i in range(3)],
            ],
            {},
            (param(0, 0), param(1, 1), param(2, 2)),
        ),
        (
            [
                [param(i) for i in range(3)],
            ],
            {},
            (param(0), param(1), param(2)),
        ),
        (
            [
                ([i, 1] for i in range(3)),
            ],
            {"gap_max_score": 5},
            (
                param(0, 1, gap_max_score=5),
                param(1, 1, gap_max_score=5),
                param(2, 1, gap_max_score=5),
            ),
        ),
        (
            [
                (param(i, gap_hidden=i % 2 == 0) for i in range(3)),
            ],
            {"gap_max_score": 5},
            (
                param(0, gap_max_score=5, gap_hidden=True),
                param(1, gap_max_score=5, gap_hidden=False),
                param(2, gap_max_score=5, gap_hidden=True),
            ),
        ),
        (
            [
                (param(i, gap_hidden=i % 2 == 0) for i in range(3)),
            ],
            {"gap_max_score": 5, "gap_hidden": True},
            (
                param(0, gap_max_score=5, gap_hidden=True),
                param(1, gap_max_score=5, gap_hidden=True),
                param(2, gap_max_score=5, gap_hidden=True),
            ),
        ),
    ],
)
def test_test_params_param_iter(args, kwargs, results) -> None:
    bundle = test_cases.param_iter(*args, **kwargs)

    assert len(bundle.final_params) == len(results)
    for i, j in zip(bundle.final_params, results):
        assert i == j


@pytest.mark.parametrize(
    "args, kwargs, results",
    [
        (
            ([i for i in range(5)], [i for i in range(3)], [i for i in range(2)]),
            {},
            (param([0, 1, 2, 3, 4]), param([0, 1, 2]), param([0, 1])),
        ),
        (
            ([i for i in range(5)], [i for i in range(3)], [i for i in range(2)]),
            {"gap_hidden": True},
            (
                param([0, 1, 2, 3, 4], gap_hidden=True),
                param([0, 1, 2], gap_hidden=True),
                param([0, 1], gap_hidden=True),
            ),
        ),
        (
            (
                param([i for i in range(5)], gap_hidden=True),
                param([i for i in range(3)]),
                [i for i in range(2)],
            ),
            {},
            (
                param([0, 1, 2, 3, 4], gap_hidden=True),
                param([0, 1, 2]),
                param([0, 1]),
            ),
        ),
        (
            (
                param([i for i in range(5)], gap_hidden=True),
                param([i for i in range(3)], gap_max_score=5),
                [i for i in range(2)],
            ),
            {"gap_hidden": True},
            (
                param([0, 1, 2, 3, 4], gap_hidden=True),
                param([0, 1, 2], gap_hidden=True, gap_max_score=5),
                param([0, 1], gap_hidden=True),
            ),
        ),
    ],
)
def test_test_singular_params(args, kwargs, results) -> None:
    # singular params is expected not to unfold
    bundle = test_cases.singular_params(*args, **kwargs)

    assert len(bundle.final_params) == len(results)
    for i, j in zip(bundle.final_params, results):
        assert i == j


@pytest.mark.parametrize(
    "args, kwargs, results",
    [
        (
            ([[i, i] for i in range(3)],),
            {},
            (param([0, 0]), param([1, 1]), param([2, 2])),
        ),
        (
            [
                ([i, 1] for i in range(3)),
            ],
            {"gap_max_score": 5},
            (
                param([0, 1], gap_max_score=5),
                param([1, 1], gap_max_score=5),
                param([2, 1], gap_max_score=5),
            ),
        ),
        (
            [
                (param(i, gap_hidden=i % 2 == 0) for i in range(3)),
            ],
            {"gap_max_score": 5},
            (
                param(0, gap_max_score=5, gap_hidden=True),
                param(1, gap_max_score=5, gap_hidden=False),
                param(2, gap_max_score=5, gap_hidden=True),
            ),
        ),
        (
            [
                (param(i, gap_hidden=i % 2 == 0) for i in range(3)),
            ],
            {"gap_max_score": 5, "gap_hidden": True},
            (
                param(0, gap_max_score=5, gap_hidden=True),
                param(1, gap_max_score=5, gap_hidden=True),
                param(2, gap_max_score=5, gap_hidden=True),
            ),
        ),
    ],
)
def test_test_singular_param_iter(args, kwargs, results) -> None:
    # singular params is expected not to unfold
    bundle = test_cases.singular_param_iter(*args, **kwargs)

    assert len(bundle.final_params) == len(results)
    for i, j in zip(bundle.final_params, results):
        assert i == j
