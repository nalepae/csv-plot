from typing import Dict, IO, Iterator, List, Optional, Tuple, Union, cast
from huge_csv_reader.padded_text_file import _PaddedTextFile


class ColumnNotFoundError(Exception):
    pass


class _PaddedCSVFile:
    def __init__(
        self,
        file_descriptor: IO,
        file_size: int,
        column_and_type: List[Tuple[str, type]],
    ) -> None:
        padded_text_file = _PaddedTextFile(file_descriptor, file_size, offset=0)
        header_line = cast(str, padded_text_file[0])
        headers = header_line.split(",")

        if len(column_and_type) == 0:
            raise ValueError("`column_and_type` is an empty list")

        columns, _ = zip(*column_and_type)

        if not set(columns) <= set(headers):
            raise ColumnNotFoundError(
                "At least one column specified in `column_to_type` in not present in "
                "the file"
            )

        header_to_index = {header: index for index, header in enumerate(headers)}

        self.__column_indexes_type = [
            (header_to_index[column], type) for column, type in column_and_type
        ]

        self.padded_text_file = _PaddedTextFile(file_descriptor, file_size, offset=1)

    def __len__(self):
        return len(self.padded_text_file)

    def __getitem__(
        self, line_number_or_slice: Union[int, slice]
    ) -> Union[List, List[List]]:
        def handle_line_number(line_number: int) -> List:
            line = cast(str, self.padded_text_file[line_number])
            items = line.split(",")
            return [type(items[index]) for index, type in self.__column_indexes_type]

        def handle_slice(slice: slice) -> List[List]:
            return [
                [
                    type(items.split(",")[index])
                    for index, type in self.__column_indexes_type
                ]
                for items in self.padded_text_file[slice]
            ]

        if isinstance(line_number_or_slice, int):
            return handle_line_number(line_number_or_slice)
        elif isinstance(line_number_or_slice, slice):
            return handle_slice(line_number_or_slice)

    def get(
        self, start: Optional[int] = None, stop: Optional[int] = None
    ) -> Iterator[List]:
        for line in self.padded_text_file.get(start, stop):
            items = line.split(",")
            yield [type(items[index]) for index, type in self.__column_indexes_type]

