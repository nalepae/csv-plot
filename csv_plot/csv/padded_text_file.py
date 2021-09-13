from contextlib import contextmanager
from pathlib import Path
from typing import IO, Iterator, List, Optional, Tuple, Union

from .gettable import Gettable


class OffsetError(Exception):
    pass


class TextFileNotPaddedError(Exception):
    pass


class PaddedTextFile(Gettable):
    """Represent a padded text file, where lines are reachable with O(1) complexity.

    A padded text file is a text file where all lines have exactly the same length.
    In general, lines are right padded with white spaces.
    The last line MUST also contain a carriage return.

    Only line(s) you request will be loaded in memory.

    Usage:
    padded_text_file = PaddedTextFile(<file_descriptor>, <file_zise>, <offset>)

    # Get the number of lines
    len(padded_text_file)

    # Get the third line of the file
    padded_text_file[2]

    # Get the last line of the file
    padded_text_file[-1]

    # Get an iterator on lines between the third line (included) and the last line
    # (excluded)
    padded_text_file.get(start=2, stop=-1)

    # Get all lines between the third line (included) and the last line (excluded)
    # Warning: All lines in the selected range will be loaded into memory.
    #          For example: padded_text_file[:] will load all the file in memory.
    #          If possible, use padded_text_file.get(start=a, stop=b) instead of
    #                           padded_text_file[a, b]
    padded_text_file[2:-1]

    # Get the size (number of characters) of one line
    padded_text_file.line_size
    """

    def __init__(self, file_descriptor: IO, file_size: int, offset: int) -> None:
        """Constructor.

        file_descriptor: The file descriptor pointing to the padded CSV file
        file_size      : The file size (in bytes) of the padded CSV file pointed by
                         `file_descriptor`
        offset         : The number of first line(s) to skip. Must be >= 0

        If not 0 <= `offset` <= number of lines, an `OffsetError` is raised.

        If at least one line of the file pointed by `file_descriptor` has not the same
        length than others, a `TextFileNotPaddedError` is raised.
        """
        self.__offset = offset
        self.__file_descriptor = file_descriptor

        first_line = next(file_descriptor)

        self.line_size = len(first_line)
        self.__len = file_size // self.line_size

        if not 0 <= offset <= self.__len:
            raise OffsetError(f"Offset must be in [0;{self.__len}]")

        if file_size % self.line_size != 0:
            raise TextFileNotPaddedError("text file is not padded")

    def __get_start_and_stop(
        self,
        slice_start: Optional[int],
        slice_stop: Optional[int],
    ) -> Tuple[int, int]:
        """Get `start` and `stop`."""
        start = (
            (
                self.__offset + slice_start
                if slice_start >= 0
                else max(self.__offset, self.__len + slice_start)
            )
            if slice_start is not None
            else self.__offset
        )

        stop = (
            (
                (
                    min(slice_stop + self.__offset, self.__len)
                    if slice_stop >= 0
                    else self.__len + slice_stop
                )
            )
            if slice_stop is not None
            else self.__len
        )

        return start, stop

    def __len__(self):
        """Return the number of lines of the file."""
        return self.__len - self.__offset

    def __getitem__(
        self, line_number_or_slice: Union[int, slice]
    ) -> Union[str, List[str]]:
        """Get a given line or a given slice of lines.

        line_number_or_slice: The line number or the slice where lines will be retrieved
        """

        def handle_line_number(line_number: int) -> str:
            real_line_number = (
                line_number + self.__offset
                if line_number >= 0
                else self.__len + line_number
            )

            if not self.__offset <= real_line_number < self.__len:
                raise IndexError("list index out of range")

            self.__move_cursor(real_line_number)
            return next(self.__file_descriptor).rstrip()

        def handle_slice(slice: slice) -> List[str]:
            start, stop = self.__get_start_and_stop(slice.start, slice.stop)

            self.__move_cursor(start)
            return [next(self.__file_descriptor).rstrip() for _ in range(start, stop)]

        if isinstance(line_number_or_slice, int):
            return handle_line_number(line_number_or_slice)
        elif isinstance(line_number_or_slice, slice):
            return handle_slice(line_number_or_slice)

    def get(
        self, start: Optional[int] = None, stop: Optional[int] = None
    ) -> Iterator[str]:
        """Return an iterator on a given slice of lines.

        start: The first line of slice (included)
        stop : The last line of slice (excluded)
        """
        real_start, real_stop = self.__get_start_and_stop(start, stop)
        self.__move_cursor(real_start)

        for _ in range(real_start, real_stop):
            yield next(self.__file_descriptor).rstrip()

    def __move_cursor(self, line_number: int) -> None:
        """Move cursor of file descriptor to `line_number`.

        line_number: The line number where to move the cursor
        """
        self.__file_descriptor.seek(self.line_size * line_number, 0)


@contextmanager
def padded_text_file(path: Path, offset: int = 0) -> Iterator[PaddedTextFile]:
    """Represent a padded text file, where lines are reachable with O(1) complexity.

    A padded text file is a text file where all lines have exactly the same length.
    In general, lines are right padded with white spaces.
    The last line MUST also contain a carriage return.

    Only line(s) you request will be loaded in memory.

    Usage:
    with padded_text_file(<file_path>, <offset>) as ptf:
        # Get the number of lines
        len(ptf)

        # Get the third line of the file
        ptf[2]

        # Get the last line of the file
        ptf[-1]

        # Get an iterator on lines between the third line (included) and the last line
        # (excluded)
        ptf.get(start=2, stop=-1)

        # Get all lines between the third line (included) and the last line (excluded)
        Warning: All lines in the selected range will be loaded into memory.
                For example: ptf[:] will load all the file in memory.
                If possible, use ptf.get(start=a, stop=b) instead of ptf[a, b]
        ptf[2:-1]
    """
    try:
        with path.open() as file_descriptor:
            yield PaddedTextFile(file_descriptor, path.stat().st_size, offset)
    finally:
        pass
