import os
from pathlib import Path

from huge_csv_reader.pad_and_sample import pseudo_hash


def test_pseudo_hash(tmp_path: Path):
    path = tmp_path / "file.txt"
    with path.open("w") as file_descriptor:
        file_descriptor.write("qwerty")

    os.utime(path, (42, 42))

    assert pseudo_hash(path) == "46141dc64506ddc74fcf3cae348e0d77"
    assert pseudo_hash(path, "12345") == "ece35c8647c0fe39e450443c9514b412"
