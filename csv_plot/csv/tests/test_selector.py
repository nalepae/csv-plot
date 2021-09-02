from pathlib import Path

import pytest
from pytest import fixture

from ..selector import Selected, selector
from . import assets


@fixture
def hashed_dir() -> Path:
    return Path(assets.__file__).parent / "8bed00c4529bfd12bd70678a71eaf5af"


def test_selector(hashed_dir):
    with selector(hashed_dir, ("a", int), [("b", float), ("d", float)]) as sel:
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
            xs=[1, 9, 17],
            name_to_y={
                "b": Selected.Y(mins=[2, 10, 18], maxs=[6, 14, 18]),
                "d": Selected.Y(mins=[4, 12, 20], maxs=[8, 16, 20]),
            },
        )

        assert (
            sel[1:9:2]
            == sel[0.5:9.5:2]
            == Selected(
                xs=[1, 9],
                name_to_y={
                    "b": Selected.Y(mins=[2, 10], maxs=[6, 14]),
                    "d": Selected.Y(mins=[4, 12], maxs=[8, 16]),
                },
            )
        )
