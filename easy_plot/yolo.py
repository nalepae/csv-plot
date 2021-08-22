from datetime import datetime
from multiprocessing import Process, Queue
from multiprocessing.queues import Empty
from pathlib import Path
from threading import Thread
from typing import List, Optional, Tuple, cast

import pyqtgraph as pg

import huge_csv_reader.selector
from huge_csv_reader.pseudo_hash import pseudo_hash
from huge_csv_reader.selector import Selected

pg.setConfigOptions(antialias=True)

MARGIN = 0.2


source_csv_file = Path("/home/manu/Perso/huge_file.csv")
dir_path = Path("/home/manu/Perso") / pseudo_hash(source_csv_file, "time")
parser = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")


class Selector(Process):
    def __init__(self, request_queue: Queue, response_queue: Queue) -> None:
        super().__init__()
        self.__request_queue = request_queue
        self.__response_queue = response_queue

    def run(self) -> None:
        with huge_csv_reader.selector.selector(
            dir_path,
            ("time", parser),  # type: ignore
            [("a", float), ("b", float)],
            1000,
        ) as selector:
            selected = selector[:]
            first_x, *_ = selected.xs

            xs = (
                [x.timestamp() for x in cast(List[datetime], selected.xs)]
                if isinstance(first_x, datetime)
                else cast(List[float], selected.xs)
            )

            self.__response_queue.put((xs, selected))

            while True:
                # Retrieve an item and block if no item is available
                meaningful_item: Optional[
                    Tuple[float, float]
                ] = self.__request_queue.get()

                # Retrieve all pending items in the queue.
                # Only the last one is meaningful/
                while True:
                    try:
                        item = self.__request_queue.get(block=False)
                    except Empty:
                        break

                    meaningful_item = item

                if meaningful_item is None:
                    self.__response_queue.put(None)
                    return

                visible_start_float, visible_stop_float = meaningful_item

                visible_range = visible_stop_float - visible_start_float
                visible_range_with_margin = MARGIN * visible_range
                start_float = visible_start_float - visible_range_with_margin
                stop_float = visible_stop_float + visible_range_with_margin

                start = datetime.fromtimestamp(start_float)
                stop = datetime.fromtimestamp(stop_float)

                selected = selector[start:stop]  # type: ignore

                xs = (
                    [x.timestamp() for x in cast(List[datetime], selected.xs)]
                    if isinstance(first_x, datetime)
                    else cast(List[float], selected.xs)
                )

                self.__response_queue.put((xs, selected))


low = pg.PlotCurveItem(brush=(50, 50, 200, 100))
high = pg.PlotCurveItem(brush=(50, 50, 200, 100))
fill = pg.FillBetweenItem(curve1=low, curve2=high, brush=(255, 255, 255, 255))

request_queue: Queue = Queue()
response_queue: Queue = Queue()

app = pg.mkQApp("DateAxisItem Example")

selector = Selector(request_queue, response_queue)
selector.start()


def on_sig_x_range_changed():
    visible_range = win.visibleRange()
    visible_start_float = visible_range.left()
    visible_stop_float = visible_range.right()

    request_queue.put((visible_start_float, visible_stop_float))


def update():
    global low, high, response_queue

    while True:
        item: Optional[Tuple[List[float], Selected]] = response_queue.get()

        if item is None:
            return

        xs, selected = item
        low.setData(xs, selected.name_to_y["a"].mins)
        high.setData(xs, selected.name_to_y["a"].maxs)


update_thread = Thread(target=update)
update_thread.start()

win = pg.PlotWidget(axisItems={"bottom": pg.DateAxisItem()})

win.addItem(high)
win.addItem(low)
win.addItem(fill)
win.show()

win.sigXRangeChanged.connect(on_sig_x_range_changed)

app.exec()
request_queue.put(None)
update_thread.join()
