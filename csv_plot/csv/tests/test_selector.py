from datetime import datetime
from pathlib import Path

import pytest
from pytest import fixture

from ..selector import Selected, selector
from . import assets


@fixture
def hashed_dir() -> Path:
    return Path(assets.__file__).parent / "8bed00c4529bfd12bd70678a71eaf5af"


@fixture
def hashed_dir_datetime() -> Path:
    return Path(assets.__file__).parent / "8e473f7e2ae6e79501a25895afe3756e"


def test_selector(hashed_dir):
    with selector(hashed_dir, ("a", int), ["b", "d"]) as sel:
        with pytest.raises(ValueError):
            sel[::]

        assert sel[::100] == Selected(
            xs=[1, 5, 9, 13, 17],
            name_to_y={
                "b": Selected.Y(mins=[2, 6, 10, 14, 18], maxs=[2, 6, 10, 14, 18]),
                "d": Selected.Y(mins=[4, 8, 12, 16, 20], maxs=[4, 8, 12, 16, 20]),
            },
        )

        assert (
            sel[5:13:100]
            == sel[4.5:13.5:100]
            == Selected(
                xs=[5, 9, 13],
                name_to_y={
                    "b": Selected.Y(mins=[6, 10, 14], maxs=[6, 10, 14]),
                    "d": Selected.Y(mins=[8, 12, 16], maxs=[8, 12, 16]),
                },
            )
        )

        assert sel[::4] == Selected(
            xs=[1, 5, 9, 13, 17],
            name_to_y={
                "b": Selected.Y(mins=[2, 6, 10, 14, 18], maxs=[2, 6, 10, 14, 18]),
                "d": Selected.Y(mins=[4, 8, 12, 16, 20], maxs=[4, 8, 12, 16, 20]),
            },
        )

        assert (
            sel[5:13:4]
            == sel[4.5:13.5:4]
            == Selected(
                xs=[5, 9, 13],
                name_to_y={
                    "b": Selected.Y(mins=[6, 10, 14], maxs=[6, 10, 14]),
                    "d": Selected.Y(mins=[8, 12, 16], maxs=[8, 12, 16]),
                },
            )
        )

        assert sel[::3] == Selected(
            xs=[1, 9, 13],
            name_to_y={
                "b": Selected.Y(mins=[2, 10, 14], maxs=[6, 10, 18]),
                "d": Selected.Y(mins=[4, 12, 16], maxs=[8, 12, 20]),
            },
        )

        assert (
            sel[1:9:2]
            == sel[0.5:9.5:2]
            == Selected(
                xs=[1, 9],
                name_to_y={
                    "b": Selected.Y(mins=[2, 10], maxs=[6, 10]),
                    "d": Selected.Y(mins=[4, 12], maxs=[8, 12]),
                },
            )
        )


def test_selector_datetime(hashed_dir_datetime):
    parser = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f+00")

    with selector(hashed_dir_datetime, ("time", parser), ["price", "size"]) as sel:
        with pytest.raises(ValueError):
            sel[::]

        assert sel[::100] == Selected(
            xs=[
                datetime(2019, 8, 15, 16, 3, 6, 595000),
                datetime(2019, 8, 15, 16, 3, 6, 595000),
                datetime(2019, 8, 15, 16, 3, 6, 595000),
                datetime(2019, 8, 15, 16, 3, 6, 595000),
                datetime(2019, 8, 15, 16, 3, 6, 595000),
                datetime(2019, 8, 15, 16, 3, 18, 894000),
                datetime(2019, 8, 15, 16, 3, 18, 894000),
                datetime(2019, 8, 15, 16, 3, 21, 279000),
                datetime(2019, 8, 15, 16, 3, 21, 554000),
            ],
            name_to_y={
                "price": Selected.Y(
                    mins=[
                        0.7597,
                        0.7599,
                        0.76,
                        0.7601,
                        0.7602,
                        0.7597,
                        0.7599,
                        0.76,
                        0.76,
                    ],
                    maxs=[
                        0.7597,
                        0.7599,
                        0.76,
                        0.7601,
                        0.7602,
                        0.7597,
                        0.7599,
                        0.76,
                        0.76,
                    ],
                ),
                "size": Selected.Y(
                    mins=[
                        500.0,
                        1000.0,
                        1000.0,
                        1000.0,
                        1000.0,
                        500.0,
                        1000.0,
                        385.0,
                        500.0,
                    ],
                    maxs=[
                        500.0,
                        1000.0,
                        1000.0,
                        1000.0,
                        1000.0,
                        500.0,
                        1000.0,
                        385.0,
                        500.0,
                    ],
                ),
            },
        )
