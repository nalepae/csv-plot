from bisect import bisect_left, bisect_right
from enum import Enum
from typing import IO, Any, Iterator, List, Optional, Tuple, Union

from huge_csv_reader.padded_csv_file import _PaddedCSVFile


class Side(Enum):
    Left = "left"
    Right = "right"


class _SortedPaddedCSVFile:
    """Represent a padded CSV file with one sorted column, where all lines are reachable
    through the sorted column with O(log(n)) complexity.
    
    A padded CSV file is a CSV file where all lines have exactly the same lenght.
    In general, lines are right padded with white spaces.
    The last line MUST also contain a carriage return.    

    Only line(s) you request will be load in memory.

    Usage:
    sorted_padded_csv_file = _SortedPaddedCSVFile(<file_descriptor>,
                                                  <file_zise>,
                                                  <x_column_and_type_tuple>,
                                                  <y_column_and_type_tuples>
                                                 )

    Example: With the following file represented by <file_descriptor>:
    a,b,c,d    
    1,2,3,4    
    5,6,7,8    
    9,10,11,12 
    13,14,15,16
    17,18,19,20

    Here all columns are sorted, but in this example, only the column "c" has to be.
    sorted_padded_csv_file = _SortedPaddedCSVFile(<file_descriptor>, 
                                                  <file_size>,
                                                  ("c", int)
                                                  [("d", int), ("b", int)]
                                                 )

    # Get the number of lines
    len(sorted_padded_csv_file) # = 5    

    # Get the line corresponding to c == 7
    padded_csv_file[7] # = (3, [8, 6])

    # Get all lines corresponding to 6.5 <= c <= 15.5
    padded_csv_file[6.5:15.5] # = [(7, [8, 6]), (11, [12, 10]), (15, [16, 14])]

    Warning: All lines in the slice will be loaded into memory.
            For example: padded_csv_file[:] will load all the file in memory.

    # Get an iterator on all lines corresponding to 6.5 <= c <= 15.5
    padded_csv_file.get(start=6.5, stop=15.5)

    # Only few lines at a time are load in memory, so it is safe to do:
    padded_csv_file.get()
    """

    def __init__(
        self,
        file_descriptor_1: IO,
        file_descriptor_2: IO,
        file_size: int,
        x_and_type: Tuple[str, type],
        ys_and_types: List[Tuple[str, type]],
    ) -> None:
        """Constructor.

        file_descriptor_1: The file descriptor pointing to the padded CSV file.
        file_descriptor_2: The file descriptor pointing to the padded CSV file.
        file_size        : The total size (in bytes) of the padded CSV file pointed by
                           `file_descriptor`
        x_and_type       : A tuple containing
                           - The name of the column on which requests will be done
                           - The type of the column on which requests will be done
        ys_and_types     : A list of tuples where each tuple has:
                           - The name of the column
                           - The type of the column          
        
        If at least one line of the file pointed by `file_descriptor` has not the same
        length than others, a `TextFileNotPaddedError` is raised.
        """
        self.__x_file = _PaddedCSVFile(
            file_descriptor_1, file_size, [x_and_type], unwrap_if_one_column=True
        )

        self.__ys_file = _PaddedCSVFile(file_descriptor_2, file_size, ys_and_types)

    def __get_line_number_of(self, x: Any, side: Side) -> int:
        return {Side.Left: bisect_left, Side.Right: bisect_right}[side](
            self.__x_file, x  # type: ignore
        )

    def __get_start_stop(self, slice: slice) -> Tuple[Optional[int], Optional[int]]:
        start = (
            self.__get_line_number_of(slice.start, Side.Left)
            if slice.start is not None
            else None
        )

        stop = (
            self.__get_line_number_of(slice.stop, Side.Right)
            if slice.stop is not None
            else None
        )

        return start, stop

    def __len__(self):
        """Return the number of lines of the file (excluding the header)."""
        return len(self.__x_file)

    def __getitem__(
        self, x_or_slice: Union[Any, slice]
    ) -> Union[Tuple[Any, List], List[Tuple[Any, List]]]:
        """Get the line where `x` equals `x_or_slice`, or get all the lines where
        `slice.start <= x <= slice.stop`.
        
        line_number_or_slice: The x value(s) corresponding to the lines to retrieve
        """

        def handle_x(x: Any) -> Tuple[Any, List]:
            line_number = self.__get_line_number_of(x, Side.Left)
            closest_x = self.__x_file[line_number]

            if closest_x != x:
                raise IndexError("not found")

            ys = self.__ys_file[line_number]
            return (x, ys)

        def handle_slice(slice: slice) -> List[Tuple[Any, List]]:
            start, stop = self.__get_start_stop(slice)

            xs = self.__x_file[start:stop]
            yss = self.__ys_file[start:stop]

            return list(zip(xs, yss))

        if isinstance(x_or_slice, slice):
            return handle_slice(x_or_slice)
        else:
            return handle_x(x_or_slice)

    def get(
        self, start: Optional[Any] = None, stop: Optional[Any] = None
    ) -> Iterator[Tuple[Any, List]]:
        """Return an iterator on a given slice of lines.

        start: The value of `x` corresponding to the first line
        stop : The value of `x` corresponding to the last line
        """
        start_, stop_ = self.__get_start_stop(slice(start, stop))

        x_iterator = self.__x_file.get(start_, stop_)
        ys_iterator = self.__ys_file.get(start_, stop_)

        for x, ys in zip(x_iterator, ys_iterator):
            yield x, ys  # for line in self.padded_text_file.get(start, stop):

