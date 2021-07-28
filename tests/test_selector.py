from pathlib import Path

from huge_csv_reader.selector import selector
from pytest import fixture
from tests import assets


@fixture
def padded_file_path() -> Path:
    return Path(assets.__file__).parent / "padded.csv"


@fixture
def sampled_padded_file_path() -> Path:
    return Path(assets.__file__).parent / "sampled_padded.csv"


@fixture
def double_sampled_padded_file_path() -> Path:
    return Path(assets.__file__).parent / "double_sampled_padded.csv"


def test_selector(
    padded_file_path, sampled_padded_file_path, double_sampled_padded_file_path
):
    with selector(
        {padded_file_path, sampled_padded_file_path, double_sampled_padded_file_path},
        ("a", int),
    ) as sel:
        assert sel.get_nb_lines_between(5, 18) == {
            Path(padded_file_path): 4,
            Path(sampled_padded_file_path): 2,
            Path(double_sampled_padded_file_path): 1,
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
