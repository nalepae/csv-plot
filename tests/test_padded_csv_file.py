from huge_csv_reader.padded_csv_file import ColumnNotFoundError, _PaddedCSVFile
from pytest import fixture
from pathlib import Path

import pytest
from tests import assets
from typing import IO


@fixture
def padded_file_path() -> Path:
    return Path(assets.__file__).parent / "padded.csv"


@fixture
def padded_file_descriptor(padded_file_path: Path) -> IO:
    return padded_file_path.open()


@fixture
def padded_file_size(padded_file_path: Path) -> int:
    return padded_file_path.stat().st_size


def test_bad_columns(padded_file_descriptor: IO, padded_file_size: int) -> None:
    with pytest.raises(ColumnNotFoundError):
        _PaddedCSVFile(padded_file_descriptor, padded_file_size, [("not_present", int)])


def test_empy_column_and_type(
    padded_file_descriptor: IO, padded_file_size: int
) -> None:
    with pytest.raises(ValueError):
        _PaddedCSVFile(padded_file_descriptor, padded_file_size, [])


def test_len(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_csv_file = _PaddedCSVFile(
        padded_file_descriptor, padded_file_size, [("d", int), ("b", int)]
    )

    assert len(padded_csv_file) == 5


def test_line(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_csv_file = _PaddedCSVFile(
        padded_file_descriptor, padded_file_size, [("d", int), ("b", int)]
    )

    assert padded_csv_file[0] == [4, 2]
    assert padded_csv_file[-1] == [20, 18]


def test_slice(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_csv_file = _PaddedCSVFile(
        padded_file_descriptor, padded_file_size, [("d", int), ("b", int)]
    )

    assert (
        padded_csv_file[:]
        == list(padded_csv_file.get())
        == [[4, 2], [8, 6], [12, 10], [16, 14], [20, 18]]
    )

    assert (
        padded_csv_file[:3]
        == list(padded_csv_file.get(stop=3))
        == [[4, 2], [8, 6], [12, 10]]
    )

    assert (
        padded_csv_file[3:]
        == list(padded_csv_file.get(start=3))
        == [[16, 14], [20, 18]]
    )

    assert (
        padded_csv_file[1:4]
        == list(padded_csv_file.get(start=1, stop=4))
        == [[8, 6], [12, 10], [16, 14]]
    )

    assert (
        padded_csv_file[1:-1]
        == list(padded_csv_file.get(start=1, stop=-1))
        == [[8, 6], [12, 10], [16, 14]]
    )
