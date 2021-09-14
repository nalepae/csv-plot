from pathlib import Path
from typing import IO, List, Tuple

import pytest
from pytest import fixture

from ..padded_text_file import (
    OffsetError,
    SplittedPaddedTextFile,
    TextFileNotPaddedError,
    PaddedTextFile,
    padded_text_file,
)
from ..tests import assets


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
def splitted_padded_dir_path() -> Path:
    return Path(assets.__file__).parent / "splitted_padded_csv"


@fixture
def padded_file_descriptor(padded_file_path: Path) -> IO:
    return padded_file_path.open()


@fixture
def padded_file_size(padded_file_path: Path) -> int:
    return padded_file_path.stat().st_size


@fixture
def splitted_padded_csv_files_descriptor_size(
    splitted_padded_dir_path: Path,
) -> List[Tuple[IO, int]]:
    paths = [(splitted_padded_dir_path / f"{index}.csv") for index in range(3)]
    return [(path.open(), path.stat().st_size) for path in paths]


def test_not_padded(not_padded_file_descriptor: IO, not_padded_file_size: int) -> None:
    with pytest.raises(TextFileNotPaddedError):
        PaddedTextFile(not_padded_file_descriptor, not_padded_file_size, 0)


def test_len(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = PaddedTextFile(padded_file_descriptor, padded_file_size, 0)
    assert len(padded_text_file) == 6


def test_line(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = PaddedTextFile(padded_file_descriptor, padded_file_size, 0)

    assert padded_text_file[2] == "5,6,7,8"
    assert padded_text_file[-1] == "17,18,19,20"

    with pytest.raises(IndexError):
        padded_text_file[6]

    with pytest.raises(IndexError):
        padded_text_file[-7]


def test_slice(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = PaddedTextFile(padded_file_descriptor, padded_file_size, 0)

    assert (
        padded_text_file[:]
        == list(padded_text_file.get())
        == [
            "a,b,c,d",
            "1,2,3,4",
            "5,6,7,8",
            "9,10,11,12",
            "13,14,15,16",
            "17,18,19,20",
        ]
    )

    assert (
        padded_text_file[:3]
        == list(padded_text_file.get(stop=3))
        == [
            "a,b,c,d",
            "1,2,3,4",
            "5,6,7,8",
        ]
    )

    assert (
        padded_text_file[4:]
        == list(padded_text_file.get(start=4))
        == [
            "13,14,15,16",
            "17,18,19,20",
        ]
    )

    assert (
        padded_text_file[1:4]
        == list(padded_text_file.get(start=1, stop=4))
        == [
            "1,2,3,4",
            "5,6,7,8",
            "9,10,11,12",
        ]
    )

    assert (
        padded_text_file[1:-1]
        == list(padded_text_file.get(start=1, stop=-1))
        == [
            "1,2,3,4",
            "5,6,7,8",
            "9,10,11,12",
            "13,14,15,16",
        ]
    )


def test_padded_text_file(padded_file_path):
    with padded_text_file(padded_file_path) as pdt:
        assert pdt[2] == "5,6,7,8"


def test_len_offset(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = PaddedTextFile(padded_file_descriptor, padded_file_size, 1)
    assert len(padded_text_file) == 5


def test_line_offset(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = PaddedTextFile(padded_file_descriptor, padded_file_size, 1)

    assert padded_text_file[2] == "9,10,11,12"
    assert padded_text_file[-1] == "17,18,19,20"

    with pytest.raises(IndexError):
        padded_text_file[5]

    with pytest.raises(IndexError):
        padded_text_file[-6]


def test_slice_offset(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = PaddedTextFile(padded_file_descriptor, padded_file_size, 1)

    assert (
        padded_text_file[:]
        == padded_text_file[-1000:1000]
        == list(padded_text_file.get())
        == [
            "1,2,3,4",
            "5,6,7,8",
            "9,10,11,12",
            "13,14,15,16",
            "17,18,19,20",
        ]
    )

    assert (
        padded_text_file[:3]
        == padded_text_file[-5:3]
        == list(padded_text_file.get(stop=3))
        == ["1,2,3,4", "5,6,7,8", "9,10,11,12"]
    )

    assert (
        padded_text_file[4:]
        == padded_text_file[-1:]
        == list(padded_text_file.get(start=4))
        == [
            "17,18,19,20",
        ]
    )

    assert (
        padded_text_file[1:4]
        == list(padded_text_file.get(start=1, stop=4))
        == ["5,6,7,8", "9,10,11,12", "13,14,15,16"]
    )

    assert (
        padded_text_file[1:-1]
        == list(padded_text_file.get(start=1, stop=-1))
        == [
            "5,6,7,8",
            "9,10,11,12",
            "13,14,15,16",
        ]
    )


def test_offset_max(padded_file_descriptor: IO, padded_file_size: int) -> None:
    padded_text_file = PaddedTextFile(padded_file_descriptor, padded_file_size, 6)
    assert len(padded_text_file) == 0

    with pytest.raises(IndexError):
        padded_text_file[0]


def test_offset_out_of_bound(padded_file_descriptor: IO, padded_file_size: int) -> None:
    with pytest.raises(OffsetError):
        PaddedTextFile(padded_file_descriptor, padded_file_size, -1)

    with pytest.raises(OffsetError):
        PaddedTextFile(padded_file_descriptor, padded_file_size, 7)


def test_splitted_padded_text_file_offset_0(
    splitted_padded_csv_files_descriptor_size: List[Tuple[IO, int]]
):

    splitted_padded_text_file = SplittedPaddedTextFile(
        splitted_padded_csv_files_descriptor_size, offset=0
    )

    assert len(splitted_padded_text_file) == 6

    assert splitted_padded_text_file[:] == [
        "a,b,c,d",
        "1,2,3,4",
        "5,6,7,8",
        "9,10,11,12",
        "13,14,15,16",
        "17,18,19,20",
    ]

    assert splitted_padded_text_file[-1] == "17,18,19,20"
    assert splitted_padded_text_file[-1:] == ["17,18,19,20"]


def test_splitted_padded_text_file_offset_1(
    splitted_padded_csv_files_descriptor_size: List[Tuple[IO, int]]
):

    splitted_padded_text_file = SplittedPaddedTextFile(
        splitted_padded_csv_files_descriptor_size, offset=1
    )

    assert len(splitted_padded_text_file) == 5

    assert splitted_padded_text_file[:] == [
        "1,2,3,4",
        "5,6,7,8",
        "9,10,11,12",
        "13,14,15,16",
        "17,18,19,20",
    ]

    assert splitted_padded_text_file[-1] == "17,18,19,20"
    assert splitted_padded_text_file[-1:] == ["17,18,19,20"]
