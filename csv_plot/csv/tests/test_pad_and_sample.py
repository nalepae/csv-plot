import filecmp
import os
from pathlib import Path
from shutil import copy2

import pytest
from ..pad_and_sample import (
    pad,
    pad_and_sample,
    pseudo_hash,
    sample,
    sample_sampled,
)
from ..tests import assets
from pytest import fixture


@fixture
def padded_file_path() -> Path:
    return Path(assets.__file__).parent / "padded.csv"


@fixture
def sampled_file_path() -> Path:
    return Path(assets.__file__).parent / "sampled.csv"


@fixture
def double_sampled_file_path() -> Path:
    return Path(assets.__file__).parent / "double_sampled.csv"


@fixture
def sampled_no_x_file_path() -> Path:
    return Path(assets.__file__).parent / "sampled_no_x.csv"


@fixture
def sampled_multiple_x_file_path() -> Path:
    return Path(assets.__file__).parent / "sampled_multiple_x.csv"


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
    copy2(not_padded_file_path, tmpdir)

    pad(tmpdir / "not_padded.csv")
    assert filecmp.cmp(tmpdir / "not_padded.csv", padded_file_path)

    pad(tmpdir / "not_padded.csv")
    assert filecmp.cmp(tmpdir / "not_padded.csv", padded_file_path)


def test_pseudo_hash(tmp_path: Path):
    path = tmp_path / "file.txt"
    with path.open("w") as file_descriptor:
        file_descriptor.write("qwerty")

    os.utime(path, (42, 42))

    assert pseudo_hash(path) == "46141dc64506ddc74fcf3cae348e0d77"
    assert pseudo_hash(path, "12345") == "ece35c8647c0fe39e450443c9514b412"


def test_sample(tmpdir, not_padded_file_path, sampled_file_path):
    sample(
        not_padded_file_path,
        tmpdir / "output.csv",
        "a",
        [("b", float), ("d", float)],
        2,
    )

    assert filecmp.cmp(tmpdir / "output.csv", sampled_file_path)


def test_sample_not_float(tmpdir, not_padded_file_path):
    with pytest.raises(ValueError):
        sample(
            not_padded_file_path,
            tmpdir / "output.csv",
            "a",
            [("b", str), ("d", float)],
            2,
        )


def test_sample_bad_x(tmpdir, not_padded_file_path):
    with pytest.raises(IndexError):
        sample(
            not_padded_file_path,
            tmpdir / "output.csv",
            "not_existing",
            [("b", float), ("d", float)],
            2,
        )


def test_sample_bad_y(tmpdir, not_padded_file_path):
    with pytest.raises(IndexError):
        sample(
            not_padded_file_path,
            tmpdir / "output.csv",
            "a",
            [("b", float), ("not_existing", float)],
            2,
        )


def test_sample_sampled(tmpdir, sampled_file_path, double_sampled_file_path):
    sample_sampled(sampled_file_path, tmpdir / "output.csv", 2)
    assert filecmp.cmp(tmpdir / "output.csv", double_sampled_file_path)


def test_sample_sampled_no_x(tmpdir, sampled_no_x_file_path):
    with pytest.raises(ValueError):
        sample_sampled(sampled_no_x_file_path, tmpdir / "output.csv", 2)


def test_sample_sampled_multiple_x(tmpdir, sampled_multiple_x_file_path):
    with pytest.raises(ValueError):
        sample_sampled(sampled_multiple_x_file_path, tmpdir / "output.csv", 2)


def test_pad_and_sample(
    tmp_path: Path, not_padded_file_path: Path, _0: Path, _1: Path, _2: Path, _3: Path
):
    paths = {
        tmp_path / "8bed00c4529bfd12bd70678a71eaf5af" / f"{index}.csv"
        for index in range(4)
    }

    assert (
        pad_and_sample(
            not_padded_file_path, tmp_path, "a", [("b", float), ("d", float)]
        )
        == paths
    )

    assert filecmp.cmp(tmp_path / "8bed00c4529bfd12bd70678a71eaf5af" / "0.csv", _0)
    assert filecmp.cmp(tmp_path / "8bed00c4529bfd12bd70678a71eaf5af" / "1.csv", _1)
    assert filecmp.cmp(tmp_path / "8bed00c4529bfd12bd70678a71eaf5af" / "2.csv", _2)
    assert filecmp.cmp(tmp_path / "8bed00c4529bfd12bd70678a71eaf5af" / "3.csv", _3)

    assert (
        pad_and_sample(
            not_padded_file_path, tmp_path, "a", [("b", float), ("d", float)]
        )
        == paths
    )
