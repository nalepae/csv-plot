import filecmp
from pathlib import Path
from shutil import copy2

import pytest
from huge_csv_reader.sample import sample, sample_sampled
from pytest import fixture

from tests import assets


@fixture
def not_padded_file_path() -> Path:
    return Path(assets.__file__).parent / "not_padded.csv"


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
