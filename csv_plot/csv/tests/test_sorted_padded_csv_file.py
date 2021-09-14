from pathlib import Path
from typing import IO

import pytest
from pytest import fixture

from ..sorted_padded_csv_file import _SortedPaddedCSVFile, sorted_padded_csv_file
from . import assets


@fixture
def padded_file_path() -> Path:
    return Path(assets.__file__).parent / "padded.csv"


@fixture
def sampled_padded_file_path() -> Path:
    return Path(assets.__file__).parent / "sampled_padded.csv"


@fixture
def double_sampled_padded_file_path() -> Path:
    return Path(assets.__file__).parent / "double_sampled_padded.csv"


@fixture
def padded_file_descriptor_1(padded_file_path: Path) -> IO:
    return padded_file_path.open()


@fixture
def padded_file_descriptor_2(padded_file_path: Path) -> IO:
    return padded_file_path.open()


@fixture
def padded_file_size(padded_file_path: Path) -> int:
    return padded_file_path.stat().st_size


def test_len(
    padded_file_descriptor_1: IO, padded_file_descriptor_2: IO, padded_file_size: int
) -> None:
    sorted_padded_csv_file = _SortedPaddedCSVFile(
        [(padded_file_descriptor_1, padded_file_descriptor_2, padded_file_size)],
        ("c", int),
        [("d", int), ("b", int)],
    )

    assert len(sorted_padded_csv_file) == 5


def test_line(
    padded_file_descriptor_1: IO, padded_file_descriptor_2: IO, padded_file_size: int
) -> None:
    sorted_padded_csv_file = _SortedPaddedCSVFile(
        [(padded_file_descriptor_1, padded_file_descriptor_2, padded_file_size)],
        ("c", int),
        [("d", int), ("b", int)],
    )

    assert sorted_padded_csv_file[7] == (7, [8, 6])

    with pytest.raises(IndexError):
        sorted_padded_csv_file[8]


def test_slice(
    padded_file_descriptor_1: IO, padded_file_descriptor_2: IO, padded_file_size: int
) -> None:
    sorted_padded_csv_file = _SortedPaddedCSVFile(
        [(padded_file_descriptor_1, padded_file_descriptor_2, padded_file_size)],
        ("c", int),
        [("d", int), ("b", int)],
    )

    assert (
        sorted_padded_csv_file[:]
        == list(sorted_padded_csv_file.get())
        == [
            (3, [4, 2]),
            (7, [8, 6]),
            (11, [12, 10]),
            (15, [16, 14]),
            (19, [20, 18]),
        ]
    )

    assert (
        sorted_padded_csv_file[:3]
        == sorted_padded_csv_file[:3.5]  # type:ignore
        == list(sorted_padded_csv_file.get(stop=3))
        == list(sorted_padded_csv_file.get(stop=3.5))
        == [(3, [4, 2])]
    )

    assert (
        sorted_padded_csv_file[:7]
        == sorted_padded_csv_file[:7.5]  # type: ignore
        == list(sorted_padded_csv_file.get(stop=7))
        == list(sorted_padded_csv_file.get(stop=7.5))
        == [(3, [4, 2]), (7, [8, 6])]
    )

    assert (
        sorted_padded_csv_file[7:15]
        == sorted_padded_csv_file[6.5:15.5]  # type: ignore
        == list(sorted_padded_csv_file.get(start=7, stop=15))
        == list(sorted_padded_csv_file.get(start=6.5, stop=15.5))
        == [(7, [8, 6]), (11, [12, 10]), (15, [16, 14])]
    )

    assert (
        sorted_padded_csv_file[15:19]
        == sorted_padded_csv_file[14.5:42]  # type: ignore
        == list(sorted_padded_csv_file.get(start=15, stop=19))
        == list(sorted_padded_csv_file.get(start=14.5, stop=42))
        == [(15, [16, 14]), (19, [20, 18])]
    )


def test_number_of_lines_between(
    padded_file_descriptor_1: IO, padded_file_descriptor_2: IO, padded_file_size: int
) -> None:
    sorted_padded_csv_file = _SortedPaddedCSVFile(
        [(padded_file_descriptor_1, padded_file_descriptor_2, padded_file_size)],
        ("c", int),
        [("d", int), ("b", int)],
    )

    assert sorted_padded_csv_file.number_of_lines_between() == 5

    assert (
        sorted_padded_csv_file.number_of_lines_between(stop=3)
        == sorted_padded_csv_file.number_of_lines_between(stop=3.5)
        == 1
    )

    assert (
        sorted_padded_csv_file.number_of_lines_between(stop=7)
        == sorted_padded_csv_file.number_of_lines_between(stop=7.5)
        == 2
    )

    assert (
        sorted_padded_csv_file.number_of_lines_between(start=7, stop=15)
        == sorted_padded_csv_file.number_of_lines_between(start=6.5, stop=15.5)
        == 3
    )

    assert (
        sorted_padded_csv_file.number_of_lines_between(start=15, stop=19)
        == sorted_padded_csv_file.number_of_lines_between(start=14.5, stop=42)
        == 2
    )


def test_sorted_padded_csv_file(padded_file_path):
    with sorted_padded_csv_file(
        padded_file_path,
        ("c", int),
        [("d", int), ("b", int)],
    ) as spcf:
        assert (
            spcf[15:19]
            == spcf[14.5:42]  # type: ignore
            == list(spcf.get(start=15, stop=19))
            == list(spcf.get(start=14.5, stop=42))
            == [(15, [16, 14]), (19, [20, 18])]
        )
