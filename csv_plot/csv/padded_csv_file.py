from contextlib import contextmanager
from pathlib import Path
from typing import IO, Any, Iterator, List, Optional, Tuple, Union, cast

from .gettable import Gettable
from .padded_text_file import SplittedPaddedTextFile


class ColumnNotFoundError(Exception):
    pass


class _PaddedCSVFile(Gettable):
    """Represent a padded CSV file, where lines are reachable with O(1) complexity.

    A padded CSV file is a CSV file where all lines have exactly the same length.
    In general, lines are right padded with white spaces.
    The last line MUST also contain a carriage return.

    Only line(s) you request will be load in memory.

    Usage:
    padded_csv_file = _PaddedCSVFile(<files_descriptor_and_size>,
                                     <file_zise>,
                                     <column_and_type_tuples>
                                    )

    Example: With the following file represented by <files_descriptor_and_size>:
    a,b,c,d
    1,2,3,4
    5,6,7,8
    9,10,11,12
    13,14,15,16
    17,18,19,20

    padded_csv_file = _PaddedCSVFile(<files_descriptor_and_size>,
                                     <file_size>,
                                     [("d", int), ("b", int)]
                                    )

    # Get the number of lines
    len(padded_csv_file) # = 5

    # Get the third line of the file
    padded_csv_file[2] # = [12, 10]

    # Get the last line of the file
    padded_csv_file[-1] # = [20, 18]

    # Get an iterator on lines between the third line (included) and the last line
    # (excluded)
    padded_csv_file.get(start=2, stop=-1)

    # Get all lines between the third line (included) and the last line (excluded)
    # Warning: All lines in the selected range will be loaded into memory.
    #          For example: padded_csv_file[:] will load all the file in memory.
    #          If possible, use padded_csv_file.get(start=a, stop=b) instead of
    #                           padded_csv_file[a, b]
    padded_csv_file[2:-1] # = [[12, 10], [16, 14]]
    """

    def __init__(
        self,
        files_descriptor_and_size: List[Tuple[IO, int]],
        columns_and_types: List[Tuple[str, type]],
        unwrap_if_one_column=False,
    ) -> None:
        """Constructor.

        files_descriptor_and_size:
            A liste of tuples like:
                - The file descriptor pointing to the padded CSV file
                - The size (in bytes) of th padded CSV file pointed by the file
                  descriptor
        columns_and_types: A list of tuples where each tuple has:
                           - The name of the column
                           - The type of the column
        unwrap_if_one_column: Unwrap if only one column unwrap result.
                              Exemple: Instead of returning [[4], [5], [2]] return
                                       [4, 5, 2]

        If at least one line of the file pointed by `file_descriptor` has not the same
        length than others, a `TextFileNotPaddedError` is raised.
        """
        padded_text_file = SplittedPaddedTextFile(files_descriptor_and_size, offset=0)
        header_line = cast(str, padded_text_file[0])
        headers = header_line.split(",")

        if columns_and_types == []:
            raise ValueError("`column_and_type` is an empty list")

        columns, _ = zip(*columns_and_types)

        if not set(columns) <= set(headers):
            raise ColumnNotFoundError(
                "At least one column specified in `column_to_type` in not present in "
                "the file"
            )

        header_to_index = {header: index for index, header in enumerate(headers)}

        self.__column_indexes_type = [
            (header_to_index[column], type) for column, type in columns_and_types
        ]

        self.__padded_text_file = SplittedPaddedTextFile(
            files_descriptor_and_size, offset=1
        )
        _, *others = columns_and_types
        self.__has_to_unwrap = unwrap_if_one_column and others == []

    def __len__(self):
        """Return the number of lines of the file (excluding the header)."""
        return len(self.__padded_text_file)

    def __getitem__(
        self, line_number_or_slice: Union[int, slice]
    ) -> Union[Any, List, List[List]]:
        """Get given values or a given slice of values.

        line_number_or_slice: The line number or the slice where values will be
                              retrieved
        """

        def handle_line_number(line_number: int) -> Union[Any, List]:
            line = cast(str, self.__padded_text_file[line_number])
            items = line.split(",")

            return self.__unwrap_if_needed_single(
                [type(items[index]) for index, type in self.__column_indexes_type]
            )

        def handle_slice(slice: slice) -> List[Union[Any, List]]:
            return self.__unwrap_if_needed_multi(
                [
                    [
                        type(items.split(",")[index])
                        for index, type in self.__column_indexes_type
                    ]
                    for items in self.__padded_text_file[slice]
                ]
            )

        if isinstance(line_number_or_slice, int):
            return handle_line_number(line_number_or_slice)
        elif isinstance(line_number_or_slice, slice):
            return handle_slice(line_number_or_slice)

    def __unwrap_if_needed_single(self, items: List) -> Union[List, Any]:
        if self.__has_to_unwrap:
            item, *trash = items
            assert trash == []
            return item
        return items

    def __unwrap_if_needed_multi(self, items: List[List]) -> List:
        return (
            [item for sublist in items for item in sublist]
            if self.__has_to_unwrap
            else items
        )

    def get(
        self, start: Optional[int] = None, stop: Optional[int] = None
    ) -> Iterator[List]:
        """Return an iterator on a given slice of lines.

        start: The first line of slice (included)
        stop : The last line of slice (excluded)
        """
        for line in self.__padded_text_file.get(start, stop):
            items = line.split(",")
            toto = [type(items[index]) for index, type in self.__column_indexes_type]
            yield self.__unwrap_if_needed_single(toto)


@contextmanager
def padded_csv_file(
    path: Path, columns_and_types: List[Tuple[str, type]]
) -> Iterator[_PaddedCSVFile]:
    """Represent a padded CSV file, where lines are reachable with O(1) complexity.

    A padded CSV file is a CSV file where all lines have exactly the same length.
    In general, lines are right padded with white spaces.
    The last line MUST also contain a carriage return.

    Only line(s) you request will be load in memory.

    Usage:
    with padded_csv_file(<file_path>, <columns_and_types>) as pcf:
        ...

    Example: With the following file represented by <file_descriptor>:
    a,b,c,d
    1,2,3,4
    5,6,7,8
    9,10,11,12
    13,14,15,16
    17,18,19,20

    with padded_csv_file(<file_path>, [("d", int), ("b", int)]) as pcf:
        # Get the number of lines
        len(pcf) # = 5

        # Get the third line of the file
        pcf[2] # = [12, 10]

        # Get the last line of the file
        pcf[-1] # = [20, 18]

        # Get an iterator on lines between the third line (included) and the last line
        # (excluded)
        pcf.get(start=2, stop=-1)

        # Get all lines between the third line (included) and the last line (excluded)
        # Warning: All lines in the selected range will be loaded into memory.
        #          For example: padded_csv_file[:] will load all the file in memory.
        #          If possible, use pcf.get(start=a, stop=b) instead of
        #                           pcf[a, b]
        pcf[2:-1] # = [[12, 10], [16, 14]]
    """
    try:
        with path.open() as file_descriptor:
            yield _PaddedCSVFile(
                [(file_descriptor, path.stat().st_size)], columns_and_types
            )
    finally:
        pass
