import filecmp
import os
from pathlib import Path

from huge_csv_reader.pad_and_sample import pad_and_sample, pseudo_hash
from pytest import fixture

from tests import assets


def test_pseudo_hash(tmp_path: Path):
    path = tmp_path / "file.txt"
    with path.open("w") as file_descriptor:
        file_descriptor.write("qwerty")

    os.utime(path, (42, 42))

    assert pseudo_hash(path) == "46141dc64506ddc74fcf3cae348e0d77"
    assert pseudo_hash(path, "12345") == "ece35c8647c0fe39e450443c9514b412"


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
