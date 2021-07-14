import filecmp
from pathlib import Path
from shutil import copy2

import pytest
from huge_csv_reader.sample import sample
from pytest import fixture

from tests import assets


@fixture
def not_padded_file_path() -> Path:
    return Path(assets.__file__).parent / "not_padded.csv"


@fixture
def sampled_file_path() -> Path:
    return Path(assets.__file__).parent / "sampled.csv"


def test_sample(tmpdir, not_padded_file_path, sampled_file_path):
    sample(
        not_padded_file_path,
        tmpdir / "output.csv",
        "a",
        [("b", float), ("d", float)],
        2,
    )

    assert filecmp.cmp(tmpdir / "output.csv", sampled_file_path)


def test_not_float(tmpdir, not_padded_file_path):
    with pytest.raises(ValueError):
        sample(
            not_padded_file_path,
            tmpdir / "output.csv",
            "a",
            [("b", str), ("d", float)],
            2,
        )


def test_bad_x(tmpdir, not_padded_file_path):
    with pytest.raises(IndexError):
        sample(
            not_padded_file_path,
            tmpdir / "output.csv",
            "not_existing",
            [("b", float), ("d", float)],
            2,
        )


def test_bad_y(tmpdir, not_padded_file_path):
    with pytest.raises(IndexError):
        sample(
            not_padded_file_path,
            tmpdir / "output.csv",
            "a",
            [("b", float), ("not_existing", float)],
            2,
        )
