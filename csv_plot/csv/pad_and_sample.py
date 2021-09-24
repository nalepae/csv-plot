import csv
import hashlib
import os
from collections import defaultdict
from pathlib import Path
from typing import IO, Dict, List, Optional, Set, Tuple

from .padded_text_file import padded_text_file


def pseudo_hash(path: Path, string: str = "") -> str:
    """Compute a pseudo hash based on :
    - The file size
    - The file last modification date
    - A given string

    (Real hash is too long to compute for big file.)
    """
    string = "-".join([str(os.path.getsize(path)), str(os.path.getmtime(path)), string])
    return str(hashlib.md5(bytes(string, "utf-8")).hexdigest())


def compute_chunks(file_path: Path, nb_chunks: int) -> List[Tuple[int, int]]:
    """Take a `file_descriptor` to a (non padded) text file, the file size and a
    number of chunks. Outputs a list of tuple.
    For each tuple, the first item represents the start byte index of a chunk, and the
    second item represents the end byte index of the same chunk.

    Example, with the following file:
    ---------------------------------

    a,b,c,d
    1,2,3,4
    5,6,7,8
    9,10,11,12
    13,14,15,16
    17,18,19,20

    compute_chunks(<path_file>, 4) == [
            (0, 16),
            (16, 35),
            (35, 47),
            (47, 59),
        ]
    """

    def get_next_new_line_byte_index(
        file_descriptor: IO, arithmetic_chunk_start: int
    ) -> int:
        file_descriptor.seek(arithmetic_chunk_start)
        return arithmetic_chunk_start + len(next(file_descriptor))

    arithmetic_chunk_size = file_path.stat().st_size / nb_chunks

    arithmetic_chunks_start = (
        int(index * arithmetic_chunk_size) - 1 for index in range(1, nb_chunks + 1)
    )

    with file_path.open() as file_descriptor:
        new_lines_byte_index_with_duplicate = [0] + [
            get_next_new_line_byte_index(file_descriptor, arithmetic_chunk_start)
            for arithmetic_chunk_start in arithmetic_chunks_start
        ]

    new_lines_byte_index = list(dict.fromkeys(new_lines_byte_index_with_duplicate))

    return list(zip(new_lines_byte_index[:-1], new_lines_byte_index[1:]))


def pad(
    input_path: Path,
    output_path: Path,
    start_byte: Optional[int] = None,
    stop_byte: Optional[int] = None,
) -> None:
    """Pad the text file (in place) pointed by `input_path` with white spaces.

    input_path: The path of the input file
    output_path: The path of the output file. If not provided, will replace the input
                 file
    """
    real_start_byte = 0 if start_byte is None else start_byte
    real_stop_byte = input_path.stat().st_size if stop_byte is None else stop_byte
    amplitude = real_stop_byte - real_start_byte

    nb_bytes_read = 0
    max_line_lenght = 0

    with input_path.open() as lines:
        lines.seek(real_start_byte)

        while nb_bytes_read < amplitude:
            line = next(lines)
            line_length = len(line.rstrip(os.linesep))
            max_line_lenght = max(line_length, max_line_lenght)
            nb_bytes_read += len(line)

    nb_bytes_read = 0

    with input_path.open() as source_lines, output_path.open("w") as dest_file:
        source_lines.seek(real_start_byte)

        while nb_bytes_read < amplitude:
            source_line = next(source_lines)
            stripped_source_line = source_line.rstrip()
            padding = max_line_lenght - len(stripped_source_line)
            dest_file.write(f"{stripped_source_line}{' '*padding}\n")
            nb_bytes_read += len(source_line)


def sample(
    source_path: Path,
    dest_path: Path,
    x: str,
    period: int,
    start_byte: Optional[int] = None,
    stop_byte: Optional[int] = None,
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

    With x == "x"

    The CSV file written in `dest_path` will be:
    x,a_min,a_max,b_min,b_max,c_min,c_max,d_min,d_max
    1,2.0,3.0,0.0,3.0,4.0,7.0,5.0,6.0
    3,4.0,8.0,0.0,7.0,4.0,7.0,6.0,8.0
    5,5.0,9.0,7.0,8.0,7.0,8.0,2.0,6.0,
    """
    real_start_byte = 0 if start_byte is None else start_byte
    real_stop_byte = source_path.stat().st_size if stop_byte is None else stop_byte
    amplitude = real_stop_byte - real_start_byte
    nb_bytes_read = 0
    line_num = 0

    with source_path.open() as source_file, dest_path.open("w") as dest_file:
        not_stripped_header_line = next(source_file)
        header_line = not_stripped_header_line.rstrip()
        headers = header_line.split(",")
        index_and_header = list(enumerate(headers))

        x_index, *trash = [index for (index, header) in index_and_header if header == x]
        y_headers = [header for header in headers if header != x]

        assert len(trash) == 0, "Multiple `x` in headers"

        if real_start_byte == 0:
            dest_headers = [x] + [
                item
                for sublist in [
                    [f"{header}_min", f"{header}_max"] for header in y_headers
                ]
                for item in sublist
            ]

            dest_file.write(f'{",".join(dest_headers)}\n')
            nb_bytes_read += len(not_stripped_header_line)
        else:
            source_file.seek(real_start_byte)

        x_value = ""

        index_to_min_max: Dict[int, Tuple[float, float]] = defaultdict(
            lambda: (float("inf"), float("-inf"))
        )

        while nb_bytes_read < amplitude:
            not_stripped_line = next(source_file)
            line = not_stripped_line.rstrip()
            values = line.split(",")

            for index, value in enumerate(values):
                if index != x_index:
                    min_, max_ = index_to_min_max[index]

                    index_to_min_max[index] = (
                        min(min_, float(value)),
                        max(max_, float(value)),
                    )

            if line_num % period == 0:
                x_value = values[x_index]

            if line_num % period == period - 1:
                dest_items = [x_value] + [
                    str(item)
                    for sublist in index_to_min_max.values()
                    for item in sublist
                ]

                dest_file.write(f'{",".join(dest_items)}\n')
                index_to_min_max = defaultdict(lambda: (float("inf"), float("-inf")))

            line_num += 1
            nb_bytes_read += len(not_stripped_line)

        if (line_num - 1) % period != period - 1:
            dest_items = [x_value] + [
                str(item) for sublist in index_to_min_max.values() for item in sublist
            ]

            dest_file.write(f'{",".join(dest_items)}\n')


def sample_sampled(
    source_path: Path, dest_path: Path, period: int, has_header: bool
) -> None:
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
        line = next(source_file)
        str_values = line.split(",")
        _, *y_values = str_values
        nb_y_values = len(y_values)
        assert nb_y_values % 2 == 0

        if has_header:
            dest_file.write(line)
        else:
            source_file.seek(0)

        x_value = ""

        values = [
            float("inf") if index % 2 == 0 else float("-inf")
            for index in range(nb_y_values)
        ]

        for line_num, line_not_stripped in enumerate(source_file):
            line = line_not_stripped.rstrip()
            str_values = line.split(",")
            x_value_temp, *y_values = str_values

            for index, value in enumerate(y_values):
                values[index] = (
                    min(float(value), values[index])
                    if index % 2 == 0
                    else max(float(value), values[index])
                )

            if line_num % period == 0:
                x_value = x_value_temp

            if line_num % period == period - 1:
                dest_items = [x_value] + [str(value) for value in values]
                dest_file.write(f'{",".join(dest_items)}\n')

                values = [
                    float("inf") if index % 2 == 0 else float("-inf")
                    for index in range(nb_y_values)
                ]

        if line_num % period != period - 1:
            dest_items = [x_value] + [str(value) for value in values]
            dest_file.write(f'{",".join(dest_items)}\n')


def pad_and_sample(
    source_csv_file_path: Path,
    dest_dir_path: Path,
    x: str,
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
        sample(source_csv_file_path, sampled_path, x, period=2)
        pad(sampled_path, padded_sampled_path)

    with padded_text_file(padded_sampled_path, offset=1) as ptf:
        nb_lines = len(ptf)

    epoch = 2

    while nb_lines > 1:
        new_sampled_path = dir_path / f"{epoch}_sampled.csv"
        new_padded_sampled_path = dir_path / f"{epoch}.csv"

        sample_sampled(sampled_path, new_sampled_path, period=2, has_header=True)
        pad(new_sampled_path, new_padded_sampled_path)

        with padded_text_file(new_padded_sampled_path, offset=1) as ptf:
            nb_lines = len(ptf)

        epoch += 1

        sampled_path = new_sampled_path

    sampled_paths = dir_path.glob("*_sampled.csv")

    for path in sampled_paths:
        path.unlink(missing_ok=True)

    return set(dir_path.glob("*.csv"))
