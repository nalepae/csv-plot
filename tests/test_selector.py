from pathlib import Path

from huge_csv_reader.selector import selector
from pytest import fixture
from tests import assets


@fixture
def hashed_dir() -> Path:
    return Path(assets.__file__).parent / "8bed00c4529bfd12bd70678a71eaf5af"


@fixture
def padded_file_path(hashed_dir: Path) -> Path:
    return hashed_dir / "0.csv"


@fixture
def sampled_padded_file_path(hashed_dir: Path) -> Path:
    return hashed_dir / "1.csv"


@fixture
def double_sampled_padded_file_path(hashed_dir: Path) -> Path:
    return hashed_dir / "2.csv"


@fixture
def triple_sampled_padded_file_path(hashed_dir: Path) -> Path:
    return hashed_dir / "3.csv"


def test_selector(
    hashed_dir,
    padded_file_path,
    sampled_padded_file_path,
    double_sampled_padded_file_path,
    triple_sampled_padded_file_path,
):
    with selector(
        hashed_dir,
        ("a", int),
    ) as sel:
        assert sel.get_nb_lines_between(5, 18) == {
            Path(padded_file_path): 4,
            Path(sampled_padded_file_path): 2,
            Path(double_sampled_padded_file_path): 1,
            Path(triple_sampled_padded_file_path): 0,
        }

        assert sel.get_max_resolution_lines_between(0, 20, 4096) == padded_file_path
        assert sel.get_max_resolution_lines_between(0, 20, 5) == padded_file_path
        assert sel.get_max_resolution_lines_between(0, 20, 4) == padded_file_path

        assert (
            sel.get_max_resolution_lines_between(0, 20, 3) == sampled_padded_file_path
        )

        assert (
            sel.get_max_resolution_lines_between(0, 20, 2)
            == double_sampled_padded_file_path
        )
