from itertools import accumulate
from typing import Any, Iterator, List, Optional, Tuple, Union

from .gettable import Gettable


class SplittedIterable:
    def __init__(self, iterables: List[Gettable], offset: int) -> None:
        iterables_lengths = [len(iterable) for iterable in iterables]

        self.__iterables = iterables
        self.__len = sum(iterables_lengths)
        self.__offset = offset

        cumulated_lengths = list(accumulate(iterables_lengths))
        shifted_cumulated_lengths = [0] + cumulated_lengths

        self.__blocks_start_stop = [
            (start, stop)
            for start, stop in zip(
                shifted_cumulated_lengths[:-1], shifted_cumulated_lengths[1:]
            )
        ]

    def __len__(self) -> int:
        return self.__len - self.__offset

    def __getitem__(self, index_or_slice: Union[int, slice]) -> Union[Any, List]:
        if isinstance(index_or_slice, int):
            block_index, item_index = self.__get_index(index_or_slice)
            return self.__iterables[block_index][item_index]
        elif isinstance(index_or_slice, slice):
            return list(self.get(index_or_slice.start, index_or_slice.stop))

    def get(self, start: Optional[int] = None, stop: Optional[int] = None) -> Iterator:
        slices = self.__get_slices(start, stop)

        iterable_slice_list = [
            (iterable, slice_)
            for iterable, slice_ in zip(self.__iterables, slices)
            if slice_ is not None
        ]

        for iterable, slice_ in iterable_slice_list:
            start, stop = slice_
            yield from iterable.get(start, stop)

    def __get_index(self, index: int) -> Tuple[int, int]:
        real_index = index + self.__offset if index >= 0 else self.__len + index

        if not self.__offset <= real_index < self.__len:
            raise IndexError("list index out of range")

        for block_index, (start, stop) in enumerate(self.__blocks_start_stop):
            if start <= real_index < stop:
                return block_index, real_index - start

        raise RuntimeError("This code should never be reached")  # pragma: no cover

    def __get_slices(
        self, slice_start: Optional[int], slice_stop: Optional[int]
    ) -> List[Optional[Tuple[Optional[int], Optional[int]]]]:
        def compute_item(
            block_start_stop: Tuple[int, int],
            slice_start_stop: Tuple[int, int],
        ) -> Optional[Tuple[Optional[int], Optional[int]]]:
            block_start, block_stop = block_start_stop
            slice_start, slice_stop = slice_start_stop

            if slice_start == slice_stop:
                return None
            elif block_start < block_stop <= slice_start < slice_stop:
                #            [ SLICE [
                # [ BLOCK [
                # ---------------------------------
                #            [ SLICE [
                #    [ BLOCK [
                return None
            elif block_start < slice_start < block_stop < slice_stop:
                #            [ SLICE [
                #        [ BLOCK [
                return slice_start - block_start, None
            elif slice_start < block_start < slice_stop < block_stop:
                #            [ SLICE [
                #                [ BLOCK [
                return None, slice_stop - block_start
            elif slice_start < slice_stop <= block_start < block_stop:
                #            [ SLICE [
                #                    [ BLOCK [
                # ---------------------------------
                #            [ SLICE [
                #                       [ BLOCK [
                return None
            elif slice_start <= block_start < block_stop <= slice_stop:
                #         [    SLICE    [
                #            [ BLOCK [
                # ---------------------------------
                #         [    SLICE [
                #            [ BLOCK [
                # ---------------------------------
                #            [ SLICE    [
                #            [ BLOCK [
                # ---------------------------------
                #            [ SLICE [
                #            [ BLOCK [

                return None, None
            elif block_start <= slice_start < slice_stop <= block_stop:
                #            [ SLICE [
                #         [    BLOCK    [
                # ---------------------------------
                #            [ SLICE [
                #         [    BLOCK [
                # ---------------------------------
                #            [ SLICE [
                #            [ BLOCK    [
                # ---------------------------------
                #            [ SLICE [
                #            [ BLOCK [
                return (
                    slice_start - block_start
                    if slice_start - block_start > 0
                    else None,
                    slice_stop - block_start if slice_stop - block_start > 0 else None,
                )

            raise RuntimeError("This code should never be reached")  # pragma: no cover

        real_slice_start = (
            (
                slice_start + self.__offset
                if slice_start >= 0
                else max(self.__offset, self.__len + slice_start)
            )
            if slice_start is not None
            else self.__offset
        )

        real_slice_stop = (
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

        real_slice_start_stop = real_slice_start, real_slice_stop

        return [
            compute_item(block_start_stop, real_slice_start_stop)
            for block_start_stop in self.__blocks_start_stop
        ]
