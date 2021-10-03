import hashlib
import os
from multiprocessing import Pool
from pathlib import Path
from typing import IO, Dict, List, Optional, Set, Tuple

from fast_pad_and_sample import pad as fast_pad
from fast_pad_and_sample import sample as fast_sample


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


def are_files_fully_sampled(dir_path: Path) -> bool:
    paths = sorted(dir_path.glob("*.csv"), key=lambda item: int(item.stem))

    for index, path in enumerate(paths):
        with path.open() as lines:
            if index == 0:
                next(lines)

            next(lines)

            try:
                next(lines)
                return False
            except StopIteration:
                pass

    return True


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
    output_path.parent.mkdir(parents=True, exist_ok=True)

    real_start_byte = 0 if start_byte is None else start_byte
    real_stop_byte = input_path.stat().st_size if stop_byte is None else stop_byte

    fast_pad(str(input_path), str(output_path), real_start_byte, real_stop_byte)


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

    def has_to_be_excluded(value: str) -> bool:
        try:
            float(value)
            return False
        except:
            return True

    real_start_byte = 0 if start_byte is None else start_byte
    real_stop_byte = source_path.stat().st_size if stop_byte is None else stop_byte

    with source_path.open() as source_file, dest_path.open("w") as dest_file:
        not_stripped_header_line = next(source_file)
        header_line = not_stripped_header_line.rstrip()
        headers = header_line.split(",")

        x_index, *trash = [index for index, header in enumerate(headers) if header == x]

        assert len(trash) == 0, "Multiple `x` in headers"

        first_line = next(source_file)
        first_line_values = first_line.split(",")

        indexes = {
            index
            for index, value in enumerate(first_line_values)
            if not has_to_be_excluded(value)
        }.union({x_index})

        y_indexes = indexes - {x_index}
        y_headers = [headers[y_index] for y_index in y_indexes]

        if real_start_byte == 0:
            dest_headers = [x] + [
                item
                for sublist in [
                    [f"{header}_min", f"{header}_max"] for header in y_headers
                ]
                for item in sublist
            ]

            dest_file.write(f'{",".join(dest_headers)}\n')

    sorted_indexes = list(indexes)
    first_index, *_ = sorted_indexes

    deltas = [first_index] + [
        right - left for left, right in zip(sorted_indexes[:-1], sorted_indexes[1:])
    ]

    fast_sample(
        str(source_path),
        str(dest_path),
        sorted_indexes.index(x_index),
        deltas,
        len(deltas),
        period,
        len(not_stripped_header_line) if real_start_byte == 0 else real_start_byte,
        real_stop_byte,
    )


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
    dest_path.parent.mkdir(parents=True, exist_ok=True)

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


def pad_to_the_end(nb_workers: int, global_dir: Path, index: int) -> None:
    current_sampled_dir = global_dir / f"{index}_sampled"

    if not current_sampled_dir.exists():
        return

    padded_dir = global_dir / f"{index}"
    sampled_paths = list(current_sampled_dir.glob("*.csv"))
    padded_paths = [padded_dir / sampled_path.name for sampled_path in sampled_paths]
    arguments = list(zip(sampled_paths, padded_paths))

    with Pool(nb_workers) as pool:
        pool.starmap(pad, arguments)

    for sampled_path in sampled_paths:
        sampled_path.unlink()

    current_sampled_dir.rmdir()
    pad_to_the_end(nb_workers, global_dir, index + 1)


def sample_sampled_to_the_end(
    nb_workers: int, sampled_global_dir: Path, index: int
) -> None:
    current_sampled_dir = sampled_global_dir / f"{index}_sampled"

    if are_files_fully_sampled(current_sampled_dir):
        return

    next_sampled_dir = sampled_global_dir / f"{(index + 1)}_sampled"
    current_sampled_paths = list(current_sampled_dir.glob("*.csv"))

    next_sampled_paths = [
        next_sampled_dir / current_sampled_path.name
        for current_sampled_path in current_sampled_paths
    ]

    arguments = [
        (current_sampled_path, next_sampled_path, 2, index == 0)
        for index, (current_sampled_path, next_sampled_path) in enumerate(
            zip(current_sampled_paths, next_sampled_paths)
        )
    ]

    with Pool(nb_workers) as pool:
        pool.starmap(sample_sampled, arguments)

    sample_sampled_to_the_end(nb_workers, sampled_global_dir, index + 1)


def pad_and_sample(
    source_csv_file_path: Path, dest_dir_path: Path, x: str, nb_workers: int
) -> bool:
    """Pad and sample `source_csv_file_path` into `dest_dir_path` with `x`.

    If the file is already sampled, this function does not resample it but exits
    immediately without error.
    """

    dir_path = dest_dir_path / pseudo_hash(source_csv_file_path, x)

    try:
        dir_path.mkdir(parents=True)
    except FileExistsError:
        return False

    padded_path = dir_path / "0"
    padded_path.mkdir(parents=True)

    sampled_path_1 = dir_path / "1_sampled"
    sampled_path_1.mkdir(parents=True)

    chunks = compute_chunks(source_csv_file_path, nb_workers)

    arguments_pad = [
        (source_csv_file_path, padded_path / f"{index}.csv", start_byte, stop_byte)
        for index, (start_byte, stop_byte) in enumerate(chunks)
    ]

    with Pool(nb_workers) as pool:
        pool.starmap(pad, arguments_pad)

    arguments_sample = [
        (
            source_csv_file_path,
            sampled_path_1 / f"{index}.csv",
            x,
            2,
            start_byte,
            stop_byte,
        )
        for index, (start_byte, stop_byte) in enumerate(chunks)
    ]

    with Pool(nb_workers) as pool:
        pool.starmap(sample, arguments_sample)

    sample_sampled_to_the_end(nb_workers, dir_path, 1)
    pad_to_the_end(nb_workers, dir_path, 1)

    return True
