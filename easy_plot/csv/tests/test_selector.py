from pathlib import Path

from pytest import fixture

from ..selector import Selected, selector
from . import assets


@fixture
def hashed_dir() -> Path:
    return Path(assets.__file__).parent / "8bed00c4529bfd12bd70678a71eaf5af"


def test_selector(hashed_dir):
    with selector(hashed_dir, ("a", int), [("b", float), ("d", float)], 100) as sel:
        assert sel[:] == Selected(
            xs=[1, 5, 9, 13, 17],
            name_to_y={
                "b": Selected.Y(mins=[2, 6, 10, 14, 18], maxs=[2, 6, 10, 14, 18]),
                "d": Selected.Y(mins=[4, 8, 12, 16, 20], maxs=[4, 8, 12, 16, 20]),
            },
        )

        assert (
            sel[5:13]
            == sel[4.5:13.5]
            == Selected(
                xs=[5, 9, 13],
                name_to_y={
                    "b": Selected.Y(mins=[6, 10, 14], maxs=[6, 10, 14]),
                    "d": Selected.Y(mins=[8, 12, 16], maxs=[8, 12, 16]),
                },
            )
        )

        sel.resolution = 4

        assert sel[:] == Selected(
            xs=[1, 5, 9, 13, 17],
            name_to_y={
                "b": Selected.Y(mins=[2, 6, 10, 14, 18], maxs=[2, 6, 10, 14, 18]),
                "d": Selected.Y(mins=[4, 8, 12, 16, 20], maxs=[4, 8, 12, 16, 20]),
            },
        )

        assert (
            sel[5:13]
            == sel[4.5:13.5]
            == Selected(
                xs=[5, 9, 13],
                name_to_y={
                    "b": Selected.Y(mins=[6, 10, 14], maxs=[6, 10, 14]),
                    "d": Selected.Y(mins=[8, 12, 16], maxs=[8, 12, 16]),
                },
            )
        )

        sel.resolution = 3

        assert sel[:] == Selected(
            xs=[1, 9, 17],
            name_to_y={
                "b": Selected.Y(mins=[2, 10, 18], maxs=[6, 14, 18]),
                "d": Selected.Y(mins=[4, 12, 20], maxs=[8, 16, 20]),
            },
        )

        sel.resolution = 2

        assert (
            sel[1:9]
            == sel[0.5:9.5]
            == Selected(
                xs=[1, 9],
                name_to_y={
                    "b": Selected.Y(mins=[2, 10], maxs=[6, 14]),
                    "d": Selected.Y(mins=[4, 12], maxs=[8, 16]),
                },
            )
        )
