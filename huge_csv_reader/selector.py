from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, Set, Tuple

from huge_csv_reader.sorted_padded_csv_file import (
    _SortedPaddedCSVFile,
    sorted_padded_csv_file,
)


class _Selector:
    """This class aims to help what sorted padded CSV file to choose regarding the
    number of lines available between start and stop.
    """

    def __init__(self, path_to_spcf: Dict[Path, _SortedPaddedCSVFile]) -> None:
        """Initializer

        path_to_spcf: A dictionary where each key is a path to a file, and where each
                      value is the correspondonding `_SortedPaddedCSVFile` object.
        """
        self.__path_to_spcf = path_to_spcf

    def get_nb_lines_between(self, start: Any, stop: Any) -> Dict[Path, int]:
        """Get the number of lines between `start` and `stop` for each file."""
        return {
            path: spcf.number_of_lines_between(start, stop)
            for path, spcf in self.__path_to_spcf.items()
        }

    def get_max_resolution_lines_between(
        self, start: Any, stop: Any, resolution: int
    ) -> Path:
        """Return the first file where the number of lines between `start` and `stop`
        is higher than `resolution`"""
        path_to_nb_lines = self.get_nb_lines_between(start, stop)
        file_max = max(path_to_nb_lines, key=path_to_nb_lines.get)

        path_to_nb_lines_filtered = {
            path: nb_lines
            for path, nb_lines in path_to_nb_lines.items()
            if nb_lines >= resolution
        }

        return (
            min(path_to_nb_lines_filtered, key=path_to_nb_lines_filtered.get)
            if len(path_to_nb_lines_filtered) > 0
            else file_max
        )


@contextmanager
def selector(dir_path: Path, x_and_type: Tuple[str, type]) -> Iterator[_Selector]:
    """Help to choose a file based on the number of lines between to X values.

    Usage:
    with selector(dir_path, ("x", float)) as select:
        select.get_nb_of_lines_between(<start>, <stop>)
        # ==> {Path1: 42, Path2: 1664, ..., Pathn: 1986}

    """
    with ExitStack() as stack:
        # TODO: Modify `sorted_padded_csv_file` so it accepts a empty list as the third
        #       argument
        path_to_spcf = {
            path: stack.enter_context(
                sorted_padded_csv_file(path, x_and_type, [x_and_type])
            )
            for path in dir_path.glob("*.csv")
        }

        yield _Selector(path_to_spcf)
