from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from itertools import groupby
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Set, Tuple, Union

from pydantic import BaseModel

from huge_csv_reader.sorted_padded_csv_file import (
    _SortedPaddedCSVFile,
    sorted_padded_csv_file,
)


class Selected(BaseModel):
    class Y(BaseModel):
        mins: List[float]
        maxs: List[float]

    xs: List[float]
    name_to_y: Dict[str, Y]


class _Selector:
    """This class aims to help what sorted padded CSV file to choose regarding the
    number of lines available between start and stop.
    """

    def __init__(
        self,
        spcf: _SortedPaddedCSVFile,
        ys_and_types: List[Tuple[str, type]],
        sampled_spcfs: Set[_SortedPaddedCSVFile],
        sampled_ys_and_types: List[Tuple[str, type]],
        resolution: int,
    ) -> None:
        self.__spcf = spcf
        self.__sampled_spcfs = sampled_spcfs
        self.__all_spcfs = self.__sampled_spcfs.union({self.__spcf})

        self.resolution = resolution
        self.__y_names = [name for name, _ in ys_and_types]
        self.__sampled_y_names = [name for name, _ in sampled_ys_and_types]

    def __get_nb_lines_between(
        self, start: Any, stop: Any
    ) -> Dict[_SortedPaddedCSVFile, int]:
        """Get the number of lines between `start` and `stop` for each Sorted Padded CSV
        file."""
        return {
            spcf: spcf.number_of_lines_between(start, stop) for spcf in self.__all_spcfs
        }

    def __get_max_resolution_lines_between(
        self, start: Any, stop: Any
    ) -> _SortedPaddedCSVFile:
        """Return the first file where the number of lines between `start` and `stop`
        is higher than `resolution`"""
        spcf_to_nb_lines = self.__get_nb_lines_between(start, stop)
        spcf_max = max(spcf_to_nb_lines, key=spcf_to_nb_lines.get)  # type: ignore

        spcf_to_nb_lines_filtered = {
            path: nb_lines
            for path, nb_lines in spcf_to_nb_lines.items()
            if nb_lines >= self.resolution
        }

        return (
            min(spcf_to_nb_lines_filtered, key=spcf_to_nb_lines_filtered.get)  # type: ignore
            if len(spcf_to_nb_lines_filtered) > 0
            else spcf_max
        )

    def __getitem__(self, x_or_slice: Union[Any, slice]) -> Selected:
        assert isinstance(x_or_slice, slice), "Only slice is supported for `x_or_slice`"

        start, stop = x_or_slice.start, x_or_slice.stop

        spcf = self.__get_max_resolution_lines_between(start, stop)
        xs, y_in_rows = zip(*spcf[start:stop])
        y_in_columns = list(zip(*y_in_rows))

        if spcf == self.__spcf:
            name_to_y = {
                y_name: Selected.Y(mins=y_in_column, maxs=y_in_column)
                for y_name, y_in_column in zip(self.__y_names, y_in_columns)
            }
        else:
            sampled_name_to_y = {
                name: y for name, y in zip(self.__sampled_y_names, y_in_columns)
            }

            name_to_y = {
                y_name: Selected.Y(
                    mins=sampled_name_to_y[f"{y_name}_min"],
                    maxs=sampled_name_to_y[f"{y_name}_max"],
                )
                for y_name in self.__y_names
            }

        return Selected(xs=xs, name_to_y=name_to_y)


@contextmanager
def selector(
    dir_path: Path,
    x_and_type: Tuple[str, type],
    ys_and_types: List[Tuple[str, type]],
    resolution: int,
) -> Iterator[_Selector]:
    name = "0.csv"

    paths = list(dir_path.glob("*.csv"))
    path, *trash = [path for path in paths if path.name == name]
    sampled_paths = [path for path in paths if path.name != name]

    assert trash == []

    sampled_ys_and_types = [
        item
        for sublist in [
            [(f"{y}_min", type), (f"{y}_max", type)] for y, type in ys_and_types
        ]
        for item in sublist
    ]

    with ExitStack() as stack:
        spcf = stack.enter_context(
            sorted_padded_csv_file(path, x_and_type, ys_and_types)
        )

        sampled_spcfs = {
            stack.enter_context(
                sorted_padded_csv_file(sampled_path, x_and_type, sampled_ys_and_types)
            )
            for sampled_path in sampled_paths
        }

        yield _Selector(
            spcf, ys_and_types, sampled_spcfs, sampled_ys_and_types, resolution
        )
