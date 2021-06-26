from typing import IO, List, Union


class TextFileNotPaddedError(Exception):
    pass


class _PaddedTextFile:
    """Represent a padded text file, where lines are reachable with O(1) complexity.
    
    A padded text file is a text file where all lines have exactly the same lenght.
    In general, lines are right padded with white spaces.
    The last line MUST also contain a carriage return.

    Only line(s) you request will be load in memory.

    Usage:
    padded_text_file = _PaddedTextFile(<file_descriptor>, <file_zise>, <offset>)

    # Get the number of lines
    len(padded_text_file)

    # Get the third line of the file
    padded_text_file[2]

    # Get the last line of the file
    padded_text_file[-1]

    # Get all lines between the third line (included) and the last line (excluded)
    padded_text_file[2:-1]

    Warning: All lines in the slice will be loaded into memory.
             For example: padded_text_file[:] will load all the file in memory
    """

    def __init__(self, file_descriptor: IO, file_size: int, offset: int) -> None:
        """Constructor.

        file_descriptor: The file descriptor pointing to the padded CSV file.
        file_size      : The total size (in bytes) of the padded CSV file pointed by
                         `file_descriptor`
        offset         : The number of first line(s) to skip. Must be >= 0.
        
        If at least one line of the file pointed by `file_descriptor` has not the same
        length than others, a `TextFileNotPaddedError` is raised.
        """
        self.__offset = offset
        self.__file_descriptor = file_descriptor

        first_line = next(file_descriptor)

        self.__line_size = len(first_line)
        self.__len = file_size // self.__line_size

        if file_size % self.__line_size != 0:
            raise TextFileNotPaddedError("text file is not padded")

    def __len__(self):
        """Return the enumber of lines of the file."""
        return self.__len

    def __getitem__(
        self, line_number_or_slice: Union[int, slice]
    ) -> Union[str, List[str]]:
        """Get a given line or a given slice of lines.
        
        line_number_or_slice: The line number or the slice to retrive lines
        """

        def handle_line_number(line_number: int) -> str:
            real_line_number = (
                line_number + self.__offset
                if line_number >= 0
                else self.__len + line_number
            )

            if not self.__offset <= real_line_number < len(self):
                raise IndexError("list index out of range")

            self.__move_cursor(real_line_number)
            return next(self.__file_descriptor).rstrip()

        def handle_slice(slice: slice) -> List[str]:
            start = (
                (
                    slice.start + self.__offset
                    if slice.start >= 0
                    else max(self.__offset, len(self) + slice.start)
                )
                if slice.start is not None
                else self.__offset
            )

            stop = (
                (
                    (
                        min(slice.stop - start + self.__offset, len(self) - start)
                        if slice.stop >= 0
                        else len(self) + slice.stop - start
                    )
                )
                if slice.stop is not None
                else len(self) - start
            )

            self.__move_cursor(start)

            return [next(self.__file_descriptor).rstrip() for _ in range(stop)]

        if isinstance(line_number_or_slice, int):
            return handle_line_number(line_number_or_slice)
        elif isinstance(line_number_or_slice, slice):
            return handle_slice(line_number_or_slice)

    def __move_cursor(self, line_number: int) -> None:
        """Move cursor of file descriptor to `line_number`.
        
        line_number: The line number where to move the cursor
        """
        self.__file_descriptor.seek(self.__line_size * line_number, 0)
