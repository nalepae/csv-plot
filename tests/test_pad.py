import filecmp
from pathlib import Path
from shutil import copy2

from huge_csv_reader.pad import pad
from pytest import fixture

from tests import assets


@fixture
def not_padded_file_path() -> Path:
    return Path(assets.__file__).parent / "not_padded.csv"


@fixture
def padded_file_path() -> Path:
    return Path(assets.__file__).parent / "padded.csv"


def test_pad(tmpdir, not_padded_file_path, padded_file_path):
    copy2(not_padded_file_path, tmpdir)

    pad(tmpdir / "not_padded.csv")
    assert filecmp.cmp(tmpdir / "not_padded.csv", padded_file_path)

    pad(tmpdir / "not_padded.csv")
    assert filecmp.cmp(tmpdir / "not_padded.csv", padded_file_path)
