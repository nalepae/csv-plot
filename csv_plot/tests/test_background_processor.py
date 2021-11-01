from datetime import datetime
from multiprocessing import Pipe
from pathlib import Path

from pytest import fixture

from ..background_processor import BackgroundProcessor
from ..tests import assets
from ..csv.selector import Selected


@fixture
def source_dir() -> Path:
    return Path(assets.__file__).parent / "8e473f7e2ae6e79501a25895afe3756e"


def test_background_processor_1(source_dir: Path):
    connector, background_connector = Pipe()

    background_processor = BackgroundProcessor(
        source_dir,
        ("time", lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f+00")),  # type: ignore
        ["size", "price"],
        background_connector,
    )

    background_processor.start()
    connector.send(None)
    background_processor.join()


def test_background_processor_2(source_dir: Path):
    connector, background_connector = Pipe()

    background_processor = BackgroundProcessor(
        source_dir,
        ("time", lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f+00")),  # type: ignore
        ["size", "price"],
        background_connector,
    )

    connector.send((None, None, 1000))
    connector.send(None)
    background_processor.start()
    background_processor.join()


def test_background_processor_3(source_dir: Path):
    connector, background_connector = Pipe()

    background_processor = BackgroundProcessor(
        source_dir,
        ("time", lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f+00")),  # type: ignore
        ["size", "price"],
        background_connector,
    )

    connector.send((None, None, 1000))
    background_processor.start()

    assert connector.recv() == (
        [
            1565877786.595,
            1565877786.595,
            1565877786.595,
            1565877786.595,
            1565877786.595,
            1565877798.894,
            1565877798.894,
            1565877801.279,
            1565877801.554,
        ],
        {
            "size": Selected.Y(
                mins=[
                    500.0,
                    1000.0,
                    1000.0,
                    1000.0,
                    1000.0,
                    500.0,
                    1000.0,
                    385.0,
                    500.0,
                ],
                maxs=[
                    500.0,
                    1000.0,
                    1000.0,
                    1000.0,
                    1000.0,
                    500.0,
                    1000.0,
                    385.0,
                    500.0,
                ],
            ),
            "price": Selected.Y(
                mins=[0.7597, 0.7599, 0.76, 0.7601, 0.7602, 0.7597, 0.7599, 0.76, 0.76],
                maxs=[0.7597, 0.7599, 0.76, 0.7601, 0.7602, 0.7597, 0.7599, 0.76, 0.76],
            ),
        },
    )
    connector.send(None)
    background_processor.join()


def test_background_processor_4(source_dir: Path):
    connector, background_connector = Pipe()

    background_processor = BackgroundProcessor(
        source_dir,
        ("time", lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f+00")),  # type: ignore
        ["size", "price"],
        background_connector,
    )

    connector.send(
        (
            1565877786.595,
            1565877801.554,
            1000,
        )
    )

    background_processor.start()
    assert connector.recv() == (
        [
            1565877786.595,
            1565877786.595,
            1565877786.595,
            1565877786.595,
            1565877786.595,
            1565877798.894,
            1565877798.894,
            1565877801.279,
            1565877801.554,
        ],
        {
            "size": Selected.Y(
                mins=[
                    500.0,
                    1000.0,
                    1000.0,
                    1000.0,
                    1000.0,
                    500.0,
                    1000.0,
                    385.0,
                    500.0,
                ],
                maxs=[
                    500.0,
                    1000.0,
                    1000.0,
                    1000.0,
                    1000.0,
                    500.0,
                    1000.0,
                    385.0,
                    500.0,
                ],
            ),
            "price": Selected.Y(
                mins=[0.7597, 0.7599, 0.76, 0.7601, 0.7602, 0.7597, 0.7599, 0.76, 0.76],
                maxs=[0.7597, 0.7599, 0.76, 0.7601, 0.7602, 0.7597, 0.7599, 0.76, 0.76],
            ),
        },
    )
    connector.send(None)
    background_processor.join()
