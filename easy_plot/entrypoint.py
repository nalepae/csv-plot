import json
from csv import DictReader
from datetime import datetime
from multiprocessing import Pipe
from pathlib import Path
from threading import Thread
from typing import Dict, Iterator, List, Optional, Tuple

import yaml
from click import Choice
from click.utils import echo
from pydantic import ValidationError
from pyqtgraph import (
    FillBetweenItem,
    GraphicsLayoutWidget,
    PlotCurveItem,
    PlotItem,
    mkQApp,
    setConfigOptions,
    DateAxisItem,
)
from pyqtgraph.graphicsItems.PlotCurveItem import PlotCurveItem
from PySide6.QtGui import QIcon
from typer import Argument, Exit, Option, Typer, colors, get_app_dir, prompt, secho

from easy_plot.csv.selector import Selected

from .background_processor import BackgroundProcessor
from .csv import pad_and_sample, pseudo_hash
from .interfaces import COLOR_NAME_TO_HEXA, Configuration

setConfigOptions(background="#141830", foreground="#D1D4DC", antialias=True)

ICON_PATH = Path(__file__).parent / "assets" / "icon-256.png"

app = Typer()

APP_DIR = Path(get_app_dir("easy-plot"))
FILES_DIR = APP_DIR / "files"
FILES_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = APP_DIR / "config.json"


def default_configuration_directory_callback(
    default_configuration_directory: Optional[Path],
):
    if default_configuration_directory:
        with CONFIG_PATH.open("w") as file_descriptor:
            json.dump(
                {
                    "default_configuration_directory": str(
                        default_configuration_directory
                    )
                },
                file_descriptor,
            )

        echo()

        secho(
            "😃 Default configuration directory set to: ",
            fg=colors.BRIGHT_GREEN,
            nl=False,
            bold=True,
        )

        secho(
            f"{default_configuration_directory} 😃",
            fg=colors.BRIGHT_GREEN,
        )

        echo()

        default_configuration_directory.mkdir(parents=True, exist_ok=True)

        raise Exit()


def get_configuration_files(configuration_files_dirs: List[Path]) -> List[Path]:
    base_files = [item for item in configuration_files_dirs if item.is_file()]
    directories = [item for item in configuration_files_dirs if item.is_dir()]

    extra_files = [
        extra_file for directory in directories for extra_file in directory.iterdir()
    ]

    return base_files + extra_files


def get_default_configuration_files() -> Iterator[Path]:
    if not CONFIG_PATH.exists():
        echo()
        secho("❌ ERROR: ", fg=colors.BRIGHT_RED, bold=True, nl=False)

        secho(
            "No configuration file provided and "
            "no default configuration directory defined ❌",
            fg=colors.BRIGHT_RED,
        )

        secho(
            "You can either give a configuration file or directory with `-c` or "
            "`--configuration-file-or-directory` option, or define default "
            "configuration directory with:",
            bold=True,
        )

        secho(
            "$ easy-plot --set-default-configuration-directory",
            bold=True,
            fg=colors.CYAN,
        )

        echo()
        raise Exit()

    with CONFIG_PATH.open("r") as file_descriptor:
        configuration = json.load(file_descriptor)
        return Path(configuration["default_configuration_directory"]).iterdir()


@app.command()
def main(
    csv_path: Path = Argument(
        ...,
        help="📜 CSV file to plot 📜",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    configuration_files_dirs: Optional[List[Path]] = Option(
        None,
        "-c",
        "--configuration-file-or-directory",
        help="📐 Configuration file or directory 📐",
        exists=True,
        file_okay=True,
        dir_okay=True,
        resolve_path=True,
        show_default=False,
    ),
    set_default_configuration_directory: Optional[Path] = Option(
        None,
        help="📐 Set default configuration directory 📐",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        is_eager=True,
        callback=default_configuration_directory_callback,
    ),
):
    """🌊 Easy Plot - Plot CSV files without headaches! 🏄"""

    # Get CSV file columns name
    with csv_path.open() as csv_file:
        reader = DictReader(csv_file)

        columns_list = reader.fieldnames

    assert columns_list is not None
    columns = set(columns_list)

    # Get configurations files
    configuration_files = (
        get_configuration_files(configuration_files_dirs)
        if configuration_files_dirs
        else get_default_configuration_files()
    )

    # Get configurations which could correspond to the CSV file
    configuration_dicts_maybe_none = (
        yaml.load(configuration_file.open("r"), Loader=yaml.FullLoader)
        for configuration_file in configuration_files
    )

    # If a YAML file is empty, then it will be parsed as `None`. It has to be filtered
    configuration_dicts = (
        configuration_dict
        for configuration_dict in configuration_dicts_maybe_none
        if configuration_dict is not None
    )

    try:
        configurations = [
            Configuration(**configuration_dict)
            for configuration_dict in configuration_dicts
        ]
    except ValidationError as e:
        secho("ERROR:", fg=colors.BRIGHT_RED, bold=True)
        secho(str(e), fg=colors.BRIGHT_RED)
        raise Exit()

    matching_configurations = [
        configuration
        for configuration in configurations
        if configuration.variables <= columns
    ]

    if len(matching_configurations) == 0:
        secho(
            "❌ ERROR: ",
            fg=colors.BRIGHT_RED,
            bold=True,
            nl=False,
        )

        secho(
            "No configuration file matching with CSV columns found ❌",
            fg=colors.BRIGHT_RED,
        )

        raise Exit()
    elif len(matching_configurations) == 1:
        chosen_configuration, *_ = matching_configurations
    else:
        secho(
            "Multiple configuration files are corresponding",
            fg=colors.BRIGHT_GREEN,
            bold=True,
        )

        for index, chosen_configuration in enumerate(matching_configurations):
            secho(
                f"{index} - {chosen_configuration.general.title}",
                fg=colors.BRIGHT_YELLOW,
            )

        choice = prompt(
            "Choose the one you want to use",
            type=Choice([str(item) for item in range(len(matching_configurations))]),
            show_choices=False,
        )

        chosen_configuration = matching_configurations[int(choice)]

    x = chosen_configuration.general.variable
    ys = columns - {x}

    secho("Process CSV file... ", fg=colors.BRIGHT_GREEN, bold=True, nl=False)

    pad_and_sample(csv_path, FILES_DIR, x, [(y, float) for y in ys])

    secho(
        "OK",
        fg=colors.BRIGHT_GREEN,
        bold=True,
    )

    win = GraphicsLayoutWidget(show=True, title=f"🌊 EASY PLOT 🏄")
    win.showMaximized()

    first_plot: Optional[PlotItem] = None
    position_to_plot: Dict[Tuple[int, int], PlotItem] = {}

    variable_to_low_high: Dict[str, Tuple[PlotCurveItem, PlotCurveItem]] = {}

    for layout_item in chosen_configuration.layout:
        plot: PlotItem = (
            win.addPlot(
                row=layout_item.x - 1,
                col=layout_item.y - 1,
                axisItems={"bottom": DateAxisItem()},
            )
            if chosen_configuration.general.date_time_format is not None
            else win.addPlot(
                row=layout_item.x - 1,
                col=layout_item.y - 1,
                axisItems={"bottom": DateAxisItem()},
            )
        )
        plot.showGrid(x=True, y=True)

        plot.setLabel(
            "bottom",
            text=chosen_configuration.general.label,
            units=chosen_configuration.general.unit,
        )

        plot.setLabel(
            "left",
            text=layout_item.label,
            units=layout_item.unit,
        )

        if first_plot is not None:
            plot.setXLink(first_plot)
        else:
            first_plot = plot

        position_to_plot[(layout_item.x, layout_item.y)] = plot

    assert first_plot is not None

    for curve in chosen_configuration.curves:
        color = COLOR_NAME_TO_HEXA[curve.color]
        low = PlotCurveItem(pen=color)
        high = PlotCurveItem(pen=color)
        fill = FillBetweenItem(low, high, color)

        plot = position_to_plot[(curve.x, curve.y)]
        plot.addItem(low)
        plot.addItem(high)
        plot.addItem(fill)

        variable_to_low_high[curve.variable] = low, high

    date_format = chosen_configuration.general.date_time_format

    parser = (
        (lambda x: datetime.strptime(x, date_format))
        if date_format is not None
        else float
    )

    connector, background_connector = Pipe()

    background_processor = BackgroundProcessor(
        FILES_DIR / pseudo_hash(csv_path, x),
        (x, parser),  # type: ignore
        list(chosen_configuration.variables),
        1000,
        background_connector,
    )

    def on_sig_x_range_changed():
        x_range, _ = first_plot.viewRange()
        x_min, x_max = x_range

        connector.send((x_min, x_max))

    def update():
        while True:
            item: Optional[Tuple[List[float], Dict[str, Selected.Y]]] = connector.recv()

            if item is None:
                return

            xs, variable_to_y = item

            for variable, y in variable_to_y.items():
                low, high = variable_to_low_high[variable]
                low.setData(xs, y.mins)
                high.setData(xs, y.maxs)

    update_thread = Thread(target=update)
    update_thread.start()

    first_plot.sigXRangeChanged.connect(on_sig_x_range_changed)

    background_processor.start()
    connector.send((None, None))

    app = mkQApp()
    app.setWindowIcon(QIcon(str(ICON_PATH)))
    app.exec()

    try:
        pass
    finally:
        connector.send(None)
