import filecmp
import os
from pathlib import Path

from pytest import fixture

from ..pad_and_sample import (
    are_files_fully_sampled,
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
def not_padded_file_path() -> Path:
    path = Path(assets.__file__).parent / "not_padded.csv"
    os.utime(path, (42, 42))
    return path


@fixture
def hashed() -> Path:
    return Path(assets.__file__).parent / "25f43600a0c028eb8b77711bc7ac3034"


@fixture
def _0(hashed: Path) -> Path:
    return hashed / "0"


@fixture
def _1(hashed: Path) -> Path:
    return hashed / "1"


@fixture
def _2(hashed: Path) -> Path:
    return hashed / "2"


@fixture
def splitted_padded_csv_path() -> Path:
    return Path(assets.__file__).parent / "splitted_padded_csv"


@fixture
def fully_splitted_padded_csv_path() -> Path:
    return Path(assets.__file__).parent / "fully_splitted_padded_csv"


def test_pad(tmpdir, not_padded_file_path, padded_file_path):
    pad(not_padded_file_path, Path(tmpdir) / "padded.csv")
    assert filecmp.cmp(tmpdir / "padded.csv", padded_file_path)


def test_pad_0_1(tmpdir, not_padded_file_path, padded_0_1_file_path):
    pad(not_padded_file_path, Path(tmpdir) / "padded.csv", 0, 20)
    assert filecmp.cmp(tmpdir / "padded.csv", padded_0_1_file_path)


def test_pad_2_4(tmpdir, not_padded_file_path, padded_2_4_file_path):
    pad(not_padded_file_path, Path(tmpdir) / "padded.csv", 20, 57)
    assert filecmp.cmp(tmpdir / "padded.csv", padded_2_4_file_path)


def test_pad_5(tmpdir, not_padded_file_path, padded_5_file_path):
    pad(not_padded_file_path, Path(tmpdir) / "padded.csv", 57, 70)
    assert filecmp.cmp(tmpdir / "padded.csv", padded_5_file_path)


def test_pseudo_hash(tmp_path: Path):
    path = tmp_path / "file.txt"
    with path.open("w") as file_descriptor:
        file_descriptor.write("qwerty")

    os.utime(path, (42, 42))

    assert pseudo_hash(path) == "46141dc64506ddc74fcf3cae348e0d77"
    assert pseudo_hash(path, "12345") == "ece35c8647c0fe39e450443c9514b412"


def test_compute_chunks(not_padded_file_path: Path):
    assert compute_chunks(not_padded_file_path, 1) == [(0, 71)]
    assert compute_chunks(not_padded_file_path, 2) == [(0, 43), (43, 71)]

    assert compute_chunks(not_padded_file_path, 4) == [
        (0, 20),
        (20, 43),
        (43, 57),
        (57, 71),
    ]

    assert compute_chunks(not_padded_file_path, 10) == [
        (0, 10),
        (10, 20),
        (20, 30),
        (30, 43),
        (43, 57),
        (57, 71),
    ]


def test_compute_chunks_padded(padded_file_path: Path):
    assert compute_chunks(padded_file_path, 1) == [(0, 84)]
    assert compute_chunks(padded_file_path, 2) == [(0, 42), (42, 84)]
    assert compute_chunks(padded_file_path, 3) == [(0, 28), (28, 56), (56, 84)]

    assert compute_chunks(padded_file_path, 6) == [
        (0, 14),
        (14, 28),
        (28, 42),
        (42, 56),
        (56, 70),
        (70, 84),
    ]


def test_are_files_fully_sampled(
    splitted_padded_csv_path: Path, fully_splitted_padded_csv_path: Path
):
    assert not are_files_fully_sampled(splitted_padded_csv_path)
    assert are_files_fully_sampled(fully_splitted_padded_csv_path)


def test_sample(tmpdir, not_padded_file_path, sampled_file_path):
    sample(
        not_padded_file_path,
        tmpdir / "output.csv",
        "a",
        2,
    )

    assert filecmp.cmp(tmpdir / "output.csv", sampled_file_path)


def test_sample_0_1(tmpdir, not_padded_file_path, sampled_0_1_file_path):
    sample(not_padded_file_path, tmpdir / "output.csv", "a", 2, 0, 20)

    assert filecmp.cmp(tmpdir / "output.csv", sampled_0_1_file_path)


def test_sample_2_4(tmpdir, not_padded_file_path, sampled_2_4_file_path):
    sample(not_padded_file_path, tmpdir / "output.csv", "a", 2, 20, 57)

    assert filecmp.cmp(tmpdir / "output.csv", sampled_2_4_file_path)


def test_sample_5(tmpdir, not_padded_file_path, sampled_5_file_path):
    sample(not_padded_file_path, tmpdir / "output.csv", "a", 2, 57, 71)

    assert filecmp.cmp(tmpdir / "output.csv", sampled_5_file_path)


def test_sample_sampled_full_header(tmpdir, sampled_0_1_file_path):
    sample_sampled(sampled_0_1_file_path, Path(tmpdir) / "output.csv", 2, True)

    assert filecmp.cmp(tmpdir / "output.csv", sampled_0_1_file_path)


def test_sample_sampled_full_no_header(tmpdir, sampled_5_file_path):
    sample_sampled(sampled_5_file_path, Path(tmpdir) / "output.csv", 2, False)

    assert filecmp.cmp(tmpdir / "output.csv", sampled_5_file_path)


def test_pad_and_sample(
    tmp_path: Path, not_padded_file_path: Path, _0: Path, _1: Path, _2: Path
):
    assert pad_and_sample(not_padded_file_path, tmp_path, "a", 2)

    assert filecmp.cmp(
        tmp_path / "25f43600a0c028eb8b77711bc7ac3034" / "0" / "0.csv", _0 / "0.csv"
    )

    assert filecmp.cmp(
        tmp_path / "25f43600a0c028eb8b77711bc7ac3034" / "0" / "1.csv", _0 / "1.csv"
    )

    assert filecmp.cmp(
        tmp_path / "25f43600a0c028eb8b77711bc7ac3034" / "1" / "0.csv", _1 / "0.csv"
    )

    assert filecmp.cmp(
        tmp_path / "25f43600a0c028eb8b77711bc7ac3034" / "1" / "1.csv", _1 / "1.csv"
    )

    assert filecmp.cmp(
        tmp_path / "25f43600a0c028eb8b77711bc7ac3034" / "2" / "0.csv", _2 / "0.csv"
    )

    assert filecmp.cmp(
        tmp_path / "25f43600a0c028eb8b77711bc7ac3034" / "2" / "1.csv", _2 / "1.csv"
    )

    assert not pad_and_sample(not_padded_file_path, tmp_path, "a", 2)
