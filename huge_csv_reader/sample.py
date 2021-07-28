from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple
import csv


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

        field_names = [field_name.strip() for field_name in reader.fieldnames]

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
