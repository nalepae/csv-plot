import csv
import hashlib
import os
from collections import defaultdict
from pathlib import Path
from shutil import copy2
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Set, Tuple

from huge_csv_reader.padded_text_file import padded_text_file


def pseudo_hash(path: Path, string: str = "") -> str:
    """Compute a pseudo hash based on :
    - The file size
    - The file last modificationdate
    - A given string

    (Real hash is too long to compute for big file.)
    """
    string = "-".join([str(os.path.getsize(path)), str(os.path.getmtime(path)), string])
    return str(hashlib.md5(bytes(string, "utf-8")).hexdigest())


def sample(
    source_path: Path,
    dest_path: Path,
    x: str,
    ys_and_types: List[Tuple[str, type]],
    period: int,
) -> None:
    """Sample a CSV file every `period` line.

    Example:
    With the following CSV corresponding to `source_path`:
    x,a,b,c,d
    1,2,3,4,5
    2,3,0,7,6
    3,4,7,4,8
    4,8,6,4,3
    5,9,8,7,6
    6,5,7,8,2

    With x == "x", ys_and_types == [("b", float), ("d", float)] and period == 3,

    The CSV file written in `dest_path` will be:
    x,d_min,d_max,b_min,b_max
    1,5.0,8.0,0.0,7.0
    4,2.0,6.0,6.0,8.0
    """
    ys = {y for y, _ in ys_and_types}

    with source_path.open() as source_file, dest_path.open("w") as dest_file:
        if {type for _, type in ys_and_types} != {float}:
            raise ValueError(
                "Only `float` is allowed as a type type for `ys_and_types`"
            )

        reader = csv.DictReader(source_file)

        if reader.fieldnames is None or x not in reader.fieldnames:
            raise IndexError(f"Variable x: {x} not found in CSV file")

        if not ys < set(reader.fieldnames):
            raise IndexError(
                f"At least on y variable is not available in the input file"
            )

        writer = csv.DictWriter(
            dest_file,
            lineterminator="\n",
            fieldnames=[x]
            + [
                item
                for sublist in [
                    [f"{y}_min", f"{y}_max"] for y in (y for y, _ in ys_and_types)
                ]
                for item in sublist
            ],
        )

        writer.writeheader()

        x_value = None
        min_values: Dict[str, float] = defaultdict(lambda: float("inf"))
        max_values: Dict[str, float] = defaultdict(lambda: float("-inf"))

        for line_num, line_dict in enumerate(reader):
            for key, value in line_dict.items():
                if key != x and key in ys:
                    min_values[key] = min(min_values[key], float(value))
                    max_values[key] = max(max_values[key], float(value))

            if line_num % period == 0:
                x_value = line_dict[x]

            if line_num % period == period - 1:
                writer.writerow(
                    {
                        **{x: x_value},
                        **{f"{key}_min": value for key, value in min_values.items()},
                        **{f"{key}_max": value for key, value in max_values.items()},
                    }
                )

                min_values = defaultdict(lambda: float("inf"))
                max_values = defaultdict(lambda: float("-inf"))

        if line_num % period != period - 1:
            writer.writerow(
                {
                    **{x: x_value},
                    **{f"{key}_min": value for key, value in min_values.items()},
                    **{f"{key}_max": value for key, value in max_values.items()},
                }
            )


def sample_sampled(source_path: Path, dest_path: Path, period: int) -> None:
    """Sample an already sampled CSV file every `period` line.

    Example:
    With the following CSV corresponding to `source_path`:
    a,b_min,b_max,d_min,d_max
    1,2.0,6.0,4.0,8.0
    9,10.0,14.0,12.0,16.0
    17,18.0,18.0,20.0,20.0

    With period == 2,

    The CSV file written in `dest_path` will be:
    a,b_min,b_max,d_min,d_max
    1,2.0,14.0,4.0,16.0
    17,18.0,18.0,20.0,20.0
    """
    with source_path.open() as source_file, dest_path.open("w") as dest_file:
        reader = csv.DictReader(source_file)

        assert reader.fieldnames

        field_names = reader.fieldnames

        xs = [
            item
            for item in field_names
            if not (item.endswith("_min") or item.endswith("_max"))
        ]

        if len(xs) == 0:
            raise ValueError("No X found in source file")

        x, *trash = xs

        if trash:
            raise ValueError("Several Xs found in source file")

        writer = csv.DictWriter(dest_file, lineterminator="\n", fieldnames=field_names)
        writer.writeheader()

        x_value = None
        min_values: Dict[str, float] = defaultdict(lambda: float("inf"))
        max_values: Dict[str, float] = defaultdict(lambda: float("-inf"))

        for line_num, line_dict in enumerate(reader):
            for key, value in line_dict.items():
                if key.endswith("_min"):
                    min_values[key] = min(min_values[key], float(value))
                elif key.endswith("_max"):
                    max_values[key] = max(max_values[key], float(value))

            if line_num % period == 0:
                x_value = line_dict[x]

            if line_num % period == period - 1:
                writer.writerow({**{x: x_value}, **min_values, **max_values})
                min_values = defaultdict(lambda: float("inf"))
                max_values = defaultdict(lambda: float("-inf"))

        if line_num % period != period - 1:
            writer.writerow({**{x: x_value}, **min_values, **max_values})


def pad(input_path: Path, output_path: Optional[Path] = None) -> None:
    """Pad the text file (in place) pointed by `input_path` with white spaces.

    input_path: The path of the input file
    output_path: The path of the output file. If not provided, will replace the input
                 file
    """
    with input_path.open() as lines:
        line_lenghts = set(len(line.rstrip(os.linesep)) for line in lines)

    if len(line_lenghts) == 1:
        # Every lines have the same lenght, so we can skip.
        # Warning: There is case where the length of two consecutive lines could sum up
        #          to the unique value of line_lengths. We choose to skip this case for
        #          now, and hope this case does not happen.
        return

    max_line_lenght = max(line_lenghts)

    with NamedTemporaryFile("w") as dest_file:
        with input_path.open() as source_lines:
            for source_line in source_lines:
                stripped_source_line = source_line.rstrip()
                padding = max_line_lenght - len(stripped_source_line)
                dest_file.write(f"{stripped_source_line}{' '*padding}\n")

        dest_file.flush()
        copy2(dest_file.name, output_path if output_path is not None else input_path)


def pad_and_sample(
    source_csv_file_path: Path,
    dest_dir_path: Path,
    x: str,
    ys_and_types: List[Tuple[str, type]],
) -> Set[Path]:
    """Pad and sample `source_csv_file_path` into `dest_dir_path` with `x`.

    If the file is already sampled, this function does not resample it but exits
    immediately without error.
    """
    # TODO: I'm not very proud of this implementation. Please do something cleaner!

    dir_path = dest_dir_path / pseudo_hash(source_csv_file_path, x)

    try:
        dir_path.mkdir(parents=True)
    except FileExistsError:
        return set(dir_path.glob("*.csv"))

    padded_path = dir_path / "0.csv"
    sampled_path = dir_path / "1_sampled.csv"
    padded_sampled_path = dir_path / "1.csv"

    pad(source_csv_file_path, padded_path)

    with padded_text_file(padded_path, offset=1) as ptf:
        nb_lines = len(ptf)

    if nb_lines > 1:
        sample(source_csv_file_path, sampled_path, x, ys_and_types, period=2)
        pad(sampled_path, padded_sampled_path)

    with padded_text_file(padded_sampled_path, offset=1) as ptf:
        nb_lines = len(ptf)

    epoch = 2

    while nb_lines > 1:
        new_sampled_path = dir_path / f"{epoch}_sampled.csv"
        new_padded_sampled_path = dir_path / f"{epoch}.csv"

        sample_sampled(sampled_path, new_sampled_path, period=2)
        pad(new_sampled_path, new_padded_sampled_path)

        with padded_text_file(new_padded_sampled_path, offset=1) as ptf:
            nb_lines = len(ptf)

        epoch += 1

        sampled_path = new_sampled_path

    sampled_paths = dir_path.glob("*_sampled.csv")

    for path in sampled_paths:
        path.unlink(missing_ok=True)

    return set(dir_path.glob("*.csv"))
