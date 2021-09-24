import filecmp
import os
from pathlib import Path

import pytest
from pytest import fixture

from ..pad_and_sample import (
    compute_chunks,
    pad,
    pad_and_sample,
    pseudo_hash,
    sample,
    sample_sampled,
)
from ..tests import assets


@fixture
def padded_file_path() -> Path:
    return Path(assets.__file__).parent / "padded.csv"


@fixture
def padded_0_1_file_path() -> Path:
    return Path(assets.__file__).parent / "padded_0_1.csv"


@fixture
def padded_2_4_file_path() -> Path:
    return Path(assets.__file__).parent / "padded_2_4.csv"


@fixture
def padded_5_file_path() -> Path:
    return Path(assets.__file__).parent / "padded_5.csv"


@fixture
def sampled_file_path() -> Path:
    return Path(assets.__file__).parent / "sampled.csv"


@fixture
def sampled_0_1_file_path() -> Path:
    return Path(assets.__file__).parent / "sampled_0_1.csv"


@fixture
def sampled_2_4_file_path() -> Path:
    return Path(assets.__file__).parent / "sampled_2_4.csv"


@fixture
def sampled_5_file_path() -> Path:
    return Path(assets.__file__).parent / "sampled_5.csv"


@fixture
def not_padded_file_path():
    path = Path(assets.__file__).parent / "not_padded.csv"
    os.utime(path, (42, 42))
    return path


@fixture
def hashed():
    return Path(assets.__file__).parent / "8bed00c4529bfd12bd70678a71eaf5af"


@fixture
def _0(hashed: Path):
    return hashed / "0.csv"


@fixture
def _1(hashed: Path):
    return hashed / "1.csv"


@fixture
def _2(hashed: Path):
    return hashed / "2.csv"


@fixture
def _3(hashed: Path):
    return hashed / "3.csv"


def test_pad(tmpdir, not_padded_file_path, padded_file_path):
    pad(not_padded_file_path, tmpdir / "padded.csv")
    assert filecmp.cmp(tmpdir / "padded.csv", padded_file_path)


def test_pad_0_1(tmpdir, not_padded_file_path, padded_0_1_file_path):
    pad(not_padded_file_path, tmpdir / "padded.csv", 0, 16)
    assert filecmp.cmp(tmpdir / "padded.csv", padded_0_1_file_path)


def test_pad_2_4(tmpdir, not_padded_file_path, padded_2_4_file_path):
    pad(not_padded_file_path, tmpdir / "padded.csv", 16, 47)
    assert filecmp.cmp(tmpdir / "padded.csv", padded_2_4_file_path)


def test_pad_5(tmpdir, not_padded_file_path, padded_5_file_path):
    pad(not_padded_file_path, tmpdir / "padded.csv", 47, 59)
    assert filecmp.cmp(tmpdir / "padded.csv", padded_5_file_path)


def test_pseudo_hash(tmp_path: Path):
    path = tmp_path / "file.txt"
    with path.open("w") as file_descriptor:
        file_descriptor.write("qwerty")

    os.utime(path, (42, 42))

    assert pseudo_hash(path) == "46141dc64506ddc74fcf3cae348e0d77"
    assert pseudo_hash(path, "12345") == "ece35c8647c0fe39e450443c9514b412"


def test_compute_chunks(not_padded_file_path: Path):
    assert compute_chunks(not_padded_file_path, 1) == [
        (0, 59),
    ]

    assert compute_chunks(not_padded_file_path, 2) == [
        (0, 35),
        (35, 59),
    ]

    assert compute_chunks(not_padded_file_path, 4) == [
        (0, 16),
        (16, 35),
        (35, 47),
        (47, 59),
    ]

    assert compute_chunks(not_padded_file_path, 10) == [
        (0, 8),
        (8, 16),
        (16, 24),
        (24, 35),
        (35, 47),
        (47, 59),
    ]


def test_compute_chunks_padded(padded_file_path: Path):
    assert compute_chunks(padded_file_path, 1) == [
        (0, 72),
    ]

    assert compute_chunks(padded_file_path, 2) == [
        (0, 36),
        (36, 72),
    ]

    assert compute_chunks(padded_file_path, 3) == [
        (0, 24),
        (24, 48),
        (48, 72),
    ]

    assert compute_chunks(padded_file_path, 6) == [
        (0, 12),
        (12, 24),
        (24, 36),
        (36, 48),
        (48, 60),
        (60, 72),
    ]


def test_sample(tmpdir, not_padded_file_path, sampled_file_path):
    sample(
        not_padded_file_path,
        tmpdir / "output.csv",
        "a",
        2,
    )

    assert filecmp.cmp(tmpdir / "output.csv", sampled_file_path)


def test_sample_0_1(tmpdir, not_padded_file_path, sampled_0_1_file_path):
    sample(not_padded_file_path, tmpdir / "output.csv", "a", 2, 0, 16)

    assert filecmp.cmp(tmpdir / "output.csv", sampled_0_1_file_path)


def test_sample_2_4(tmpdir, not_padded_file_path, sampled_2_4_file_path):
    sample(not_padded_file_path, tmpdir / "output.csv", "a", 2, 16, 47)

    assert filecmp.cmp(tmpdir / "output.csv", sampled_2_4_file_path)


def test_sample_5(tmpdir, not_padded_file_path, sampled_5_file_path):
    sample(not_padded_file_path, tmpdir / "output.csv", "a", 2, 47, 59)

    assert filecmp.cmp(tmpdir / "output.csv", sampled_5_file_path)


def test_pad_and_sample(
    tmp_path: Path, not_padded_file_path: Path, _0: Path, _1: Path, _2: Path, _3: Path
):
    paths = {
        tmp_path / "8bed00c4529bfd12bd70678a71eaf5af" / f"{index}.csv"
        for index in range(4)
    }

    assert pad_and_sample(not_padded_file_path, tmp_path, "a") == paths

    assert filecmp.cmp(tmp_path / "8bed00c4529bfd12bd70678a71eaf5af" / "0.csv", _0)
    assert filecmp.cmp(tmp_path / "8bed00c4529bfd12bd70678a71eaf5af" / "1.csv", _1)
    assert filecmp.cmp(tmp_path / "8bed00c4529bfd12bd70678a71eaf5af" / "2.csv", _2)
    assert filecmp.cmp(tmp_path / "8bed00c4529bfd12bd70678a71eaf5af" / "3.csv", _3)

    assert pad_and_sample(not_padded_file_path, tmp_path, "a") == paths
