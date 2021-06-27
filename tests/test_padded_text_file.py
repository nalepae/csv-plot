from pathlib import Path
from typing import IO

import pytest
from huge_csv_reader.padded_text_file import (
    OffsetError,
    TextFileNotPaddedError,
    _PaddedTextFile,
    padded_text_file,
)
from pytest import fixture

from tests import assets


@fixture
def not_padded_file_path() -> Path:
    return Path(assets.__file__).parent / "not_padded.csv"


@fixture
def not_padded_file_descriptor(not_padded_file_path: Path) -> IO:
    return not_padded_file_path.open()


@fixture
def not_padded_file_size(not_padded_file_path: Path) -> int:
    return not_padded_file_path.stat().st_size


@fixture
def padded_file_path() -> Path:
    return Path(assets.__file__).parent / "padded.csv"


@fixture
def padded_file_descriptor(padded_file_path: Path) -> IO:
    return padded_file_path.open()


@fixture
def padded_file_size(padded_file_path: Path) -> int:
    return padded_file_path.stat().st_size


def test_not_padded(not_padded_file_descriptor: IO, not_padded_file_size: int) -> None:
    with pytest.raises(TextFileNotPaddedError):
        _PaddedTextFile(not_padded_file_descriptor, not_padded_file_size, 0)


def test_len(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = _PaddedTextFile(padded_file_descriptor, padded_file_size, 0)
    assert len(padded_text_file) == 6


def test_line(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = _PaddedTextFile(padded_file_descriptor, padded_file_size, 0)

    assert padded_text_file[2] == "5,6,7,8"
    assert padded_text_file[-1] == "17,18,19,20"

    with pytest.raises(IndexError):
        padded_text_file[6]

    with pytest.raises(IndexError):
        padded_text_file[-7]


def test_slice(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = _PaddedTextFile(padded_file_descriptor, padded_file_size, 0)

    assert padded_text_file[:] == [
        "a,b,c,d",
        "1,2,3,4",
        "5,6,7,8",
        "9,10,11,12",
        "13,14,15,16",
        "17,18,19,20",
    ]

    assert padded_text_file[:3] == [
        "a,b,c,d",
        "1,2,3,4",
        "5,6,7,8",
    ]

    assert padded_text_file[4:] == [
        "13,14,15,16",
        "17,18,19,20",
    ]

    assert padded_text_file[1:4] == [
        "1,2,3,4",
        "5,6,7,8",
        "9,10,11,12",
    ]

    assert padded_text_file[1:-1] == [
        "1,2,3,4",
        "5,6,7,8",
        "9,10,11,12",
        "13,14,15,16",
    ]


def test_padded_text_file(padded_file_path):
    with padded_text_file(padded_file_path) as pdt:
        assert pdt[2] == "5,6,7,8"


def test_len_offset(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = _PaddedTextFile(padded_file_descriptor, padded_file_size, 1)
    assert len(padded_text_file) == 5


def test_line_offset(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = _PaddedTextFile(padded_file_descriptor, padded_file_size, 1)

    assert padded_text_file[2] == "9,10,11,12"
    assert padded_text_file[-1] == "17,18,19,20"

    with pytest.raises(IndexError):
        padded_text_file[5]

    with pytest.raises(IndexError):
        padded_text_file[-6]


def test_slice_offset(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = _PaddedTextFile(padded_file_descriptor, padded_file_size, 1)

    assert padded_text_file[:] == [
        "1,2,3,4",
        "5,6,7,8",
        "9,10,11,12",
        "13,14,15,16",
        "17,18,19,20",
    ]

    assert padded_text_file[:3] == ["1,2,3,4", "5,6,7,8", "9,10,11,12"]

    assert padded_text_file[4:] == [
        "17,18,19,20",
    ]

    assert padded_text_file[1:4] == ["5,6,7,8", "9,10,11,12", "13,14,15,16"]

    assert padded_text_file[1:-1] == [
        "5,6,7,8",
        "9,10,11,12",
        "13,14,15,16",
    ]


def test_offset_max(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = _PaddedTextFile(padded_file_descriptor, padded_file_size, 6)
    assert len(padded_text_file) == 0

    with pytest.raises(IndexError):
        padded_text_file[0]


def test_offset_out_of_bound(padded_file_descriptor: IO, padded_file_size: int) -> None:
    with pytest.raises(OffsetError):
        _PaddedTextFile(padded_file_descriptor, padded_file_size, -1)

    with pytest.raises(OffsetError):
        _PaddedTextFile(padded_file_descriptor, padded_file_size, 7)
