from contextlib import ExitStack
from datetime import datetime
from multiprocessing import Process
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, cast

from .csv import selector

MARGIN = 0.2


class BackgroundProcessor(Process):
    """Offers a way to compute - in a background process - all data needed by pyqtgraph
    from pyqtgraph visible range.

    The main (caller) process can communicate with the background process through a
    pipe.

    If several items a present in the pipe, then `BackgroundSelector` will process only
    the last one.

    Send `None` to the pipe to stop `BackgroundSelector`

    Usage:
    ------
    connection, background_connection = Pipe()

    background_processor = BackgroundProcessor(
        dir_path, ("a", int), ["b", "d"], background_connection
    )

    background_processor.start()

    connection.send((None, None, 100))
    connection.recv() == (
        [1, 5, 9, 13, 17],
        {
            "b": Selected.Y(mins=[2, 6, 10, 14, 18], maxs=[2, 6, 10, 14, 18]),
            "d": Selected.Y(mins=[4, 8, 12, 16, 20], maxs=[4, 8, 12, 16, 20]),
        }
    )

    connection.send(4.5, 13.5, 100) == (
        [5, 9, 13],
        {
            "b": Selected.Y(mins=[6, 10, 14], maxs=[6, 10, 14]),
            "d": Selected.Y(mins=[8, 12, 16], maxs=[8, 12, 16]),
        }
    )

    connection.send(None)
    """

    def __init__(
        self,
        dir_path_to_ys: Dict[Path, Set[str]],
        x_and_type: Tuple[str, type],
        connection: Connection,
    ) -> None:
        """Initializer

        dir_path  : Directory where all the files (sampled and non sampled) are located.
                    Non sampled path name's HAS to be `0.csv`

        x_and_type: Name and the type of X value
        ys        : Name of Ys types
        connection: One side of the pipe
        """
        super().__init__()
        self.__dir_path_to_ys = dir_path_to_ys
        self.__x_and_type = x_and_type
        self.__connection = connection

    def run(self) -> None:
        with ExitStack() as stack:
            dir_path_to_selector = {
                dir_path: stack.enter_context(
                    selector(dir_path, self.__x_and_type, list(ys))
                )
                for dir_path, ys in self.__dir_path_to_ys.items()
            }

            _, x_type = self.__x_and_type

            while True:
                item: Optional[
                    Tuple[Optional[float], Optional[float], int]
                ] = self.__connection.recv()

                if item is None:
                    self.__connection.send(None)
                    return

                while self.__connection.poll():
                    item = self.__connection.recv()

                    if item is None:
                        self.__connection.send(None)
                        return

                visible_start_float, visible_stop_float, resolution = item

                assert not (visible_start_float is None) != (
                    visible_stop_float is None
                ), (
                    "`visible_start_float` and `visible_stop_float` must be both set "
                    "to None or set to a value which is not None"
                )

                if visible_start_float is None and visible_stop_float is None:
                    dir_path_to_selected = {
                        dir_path: selector[::resolution]
                        for dir_path, selector in dir_path_to_selector.items()
                    }
                elif visible_start_float is not None and visible_stop_float is not None:
                    visible_range = visible_stop_float - visible_start_float
                    visible_range_with_margin = MARGIN * visible_range

                    start_float = visible_start_float - visible_range_with_margin
                    stop_float = visible_stop_float + visible_range_with_margin

                    start, stop = (
                        (
                            datetime.fromtimestamp(start_float),
                            datetime.fromtimestamp(stop_float),
                        )
                        if x_type is not float
                        else (start_float, stop_float)
                    )

                    dir_path_to_selected = {
                        dir_path: selector[start:stop:resolution]  # type: ignore
                        for dir_path, selector in dir_path_to_selector.items()
                    }
                else:
                    raise ValueError(
                        "`visible_start_float` and `visible_stop_float` must be both "
                        "set to None or set to a value which is not None"
                    )

                for dir_path, selected in dir_path_to_selected.items():
                    if len(selected.xs) == 0:
                        self.__connection.send((dir_path, [], selected.name_to_y))
                    else:
                        first_x, *_ = selected.xs

                        xs = (
                            [x.timestamp() for x in cast(List[datetime], selected.xs)]
                            if isinstance(first_x, datetime)
                            else cast(List[float], selected.xs)
                        )

                        self.__connection.send((dir_path, xs, selected.name_to_y))
