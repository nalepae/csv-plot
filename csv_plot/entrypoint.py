import json
from collections import Counter
from csv import DictReader
from datetime import datetime
from itertools import groupby
from multiprocessing import Pipe, cpu_count
from pathlib import Path
from threading import Thread
from typing import Dict, Iterator, List, Optional, Set, Tuple

import yaml  # type: ignore
from click import Choice
from click.utils import echo
from pydantic import ValidationError
from pyqtgraph import (
    DateAxisItem,
    FillBetweenItem,
    GraphicsLayoutWidget,
    PlotCurveItem,
    PlotItem,
    mkQApp,
    setConfigOptions,
)
from pyqtgraph.graphicsItems.PlotCurveItem import PlotCurveItem
from PySide6.QtGui import QIcon
from typer import Argument, Exit, Option, Typer, colors, get_app_dir, prompt, secho

from .background_processor import BackgroundProcessor
from .csv import pad_and_sample, pseudo_hash
from .csv.selector import Selected
from .interfaces import COLOR_NAME_TO_HEXA, Configuration

setConfigOptions(background="#141830", foreground="#D1D4DC", antialias=True)

ICON_PATH = Path(__file__).parent / "assets" / "icon-256.png"

app = Typer()

APP_DIR = Path(get_app_dir("csv-plot"))
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
        extra_file
        for directory in directories
        for extra_file in directory.iterdir()
        if extra_file.suffix == ".yaml"
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
            "You can either use a configuration file or directory with `-c` or "
            "`--configuration-file-or-directory` option, or define default "
            "configuration directory with:",
            bold=True,
        )

        secho(
            "$ csv-plot --set-default-configuration-directory",
            bold=True,
            fg=colors.CYAN,
        )

        echo()
        raise Exit()

    with CONFIG_PATH.open("r") as file_descriptor:
        configuration = json.load(file_descriptor)
        return (
            path
            for path in Path(configuration["default_configuration_directory"]).iterdir()
            if path.suffix == ".yaml"
        )


@app.command()
def main(
    csvs_path: List[Path] = Argument(
        ...,
        help="CSV file to plot. This file must contain a header.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    configuration_files_dirs: Optional[List[Path]] = Option(
        None,
        "-c",
        "--configuration-files-or-directories",
        help=(
            "A list of configuration files or directories containing configuration "
            "files. You can specify only one configuration file, or one directory, or "
            "mix of files and directories... If a directory is specified, CSV Plot "
            "explores recursively all subdirectories to find configuration files. If "
            "several configuration files match the CSV file, then CSV Plot ask you "
            "which one you want to use."
        ),
        exists=True,
        file_okay=True,
        dir_okay=True,
        resolve_path=True,
        show_default=False,
    ),
    set_default_configuration_directory: Optional[Path] = Option(
        None,
        help=(
            "Set a default directory where CSV Plot will recursively look for "
            "configuration files. Once done, no need to specify configuration file any "
            "more. If a configuration file is specified at launch while a default "
            "directory is specified, then the configuration file will supersede the "
            "default directory."
        ),
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        is_eager=True,
        callback=default_configuration_directory_callback,
    ),
):
    """🌊 CSV Plot - Plot CSV files without headaches! 🏄

    CSV Plot is a tool to efficiently plot your CSV files.
    You define a YAML configuration file which specify how your CSV file should be
    plotted (layout, colors, legend, units, etc...) and CSV Plot handles the heavy work
    for you.

    CSV Plot does respect your computer memory. This means CSV Plot only loads into
    memory the portion of file which has to be plotted. CSV Plot is able to plot files
    which are bigger than your memory, and has been tested with file larger than 100GB.
    """

    # Get CSV file columns names corresponding to floats
    def is_castable_to_float(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    for csv_path in set(csvs_path):
        with csv_path.open() as csv_file:
            columns_count = Counter(next(csv_file).rstrip().split(","))

        for column, count in columns_count.items():
            if count > 1:
                secho(
                    "❌ ERROR: ",
                    fg=colors.BRIGHT_RED,
                    bold=True,
                    nl=False,
                )

                secho(
                    f"In file `{csvs_path}`, the column `{column}` is present {count} times ❌",
                    fg=colors.BRIGHT_RED,
                )

                raise Exit()

    def get_columns(csv_path: Path) -> List[str]:
        with csv_path.open() as csv_file:
            reader = DictReader(csv_file)
            reader.fieldnames
            first_row = next(reader)

        return [
            column for column, value in first_row.items() if is_castable_to_float(value)
        ]

    columns_list = (get_columns(csv_path) for csv_path in set(csvs_path))
    columns = {item for sublist in columns_list for item in sublist}

    # Get configurations files
    configuration_files = (
        get_configuration_files(configuration_files_dirs)
        if configuration_files_dirs
        else get_default_configuration_files()
    )

    # Get configurations which could correspond to the CSV file
    configuration_file_to_configuration_dict_maybe_none = {
        configuration_file: yaml.load(
            configuration_file.open("r"), Loader=yaml.FullLoader
        )
        for configuration_file in configuration_files
    }

    # If a YAML file is empty, then it will be parsed as `None`. It has to be filtered
    configuration_file_to_dict = {
        configuration_file: configuration_dict
        for configuration_file, configuration_dict in configuration_file_to_configuration_dict_maybe_none.items()
        if configuration_dict is not None
    }

    try:
        configuration_file_to_configuration = {
            configuration_file: Configuration(**configuration_dict)
            for configuration_file, configuration_dict in configuration_file_to_dict.items()
        }
    except ValidationError as e:
        secho("ERROR:", fg=colors.BRIGHT_RED, bold=True)
        secho(str(e), fg=colors.BRIGHT_RED)
        raise Exit()

    matching_file_to_configuration = {
        configuration_file: configuration
        for configuration_file, configuration in configuration_file_to_configuration.items()
        if {variable for _, variable in configuration.filters_variables} <= columns
    }

    def len_0(_: Dict[Path, Configuration]) -> Tuple[Path, Configuration]:
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

    def len_1(
        matching_file_to_configuration: Dict[Path, Configuration]
    ) -> Tuple[Path, Configuration]:
        chosen_file_and_configuration, *_ = matching_file_to_configuration.items()
        return chosen_file_and_configuration

    def len_bigger_1(
        matching_file_to_configuration: Dict[Path, Configuration]
    ) -> Tuple[Path, Configuration]:
        matching_files_configurations = list(matching_file_to_configuration.items())
        matching_files, configurations = zip(*matching_files_configurations)

        secho(
            "Multiple configuration files correspond:",
            fg=colors.BRIGHT_GREEN,
            bold=True,
        )

        for index, matching_file in enumerate(matching_files):
            secho(
                f"{index} - {matching_file}",
                fg=colors.BRIGHT_YELLOW,
            )

        choice = prompt(
            "Choose which one you want to use",
            type=Choice([str(item) for item in range(len(matching_files))]),
            show_choices=False,
        )

        return matching_files[int(choice)], configurations[int(choice)]

    chosen_configuration_file, chosen_configuration = {0: len_0, 1: len_1}.get(
        len(matching_file_to_configuration), len_bigger_1
    )(matching_file_to_configuration)

    def get_column_and_path(csv_path: Path) -> List[Tuple[str, Path]]:
        with csv_path.open() as csv_file:
            reader = DictReader(csv_file)
            first_row = next(reader)

        return [
            (column, csv_path)
            for column, value in first_row.items()
            if is_castable_to_float(value)
        ]

    column_and_path_lists = (get_column_and_path(csv_path) for csv_path in csvs_path)

    column_and_path_list = (
        item for sublist in column_and_path_lists for item in sublist
    )

    column_to_path = {
        column: {path for _, path in column_and_path}
        for column, column_and_path in groupby(
            sorted(column_and_path_list), lambda x: x[0]
        )
    }

    for curve in chosen_configuration.curves:
        variable = curve.variable
        potential_files = column_to_path[variable]
        matching_files = {
            file
            for file in potential_files
            if curve.file_name_filter == None
            or str(curve.file_name_filter) in str(file)
        }

        try:
            matching_file, *trash = matching_files
        except ValueError:
            secho(
                "❌ ERROR: ",
                fg=colors.BRIGHT_RED,
                bold=True,
                nl=False,
            )

            secho(
                f"For configuration file `{chosen_configuration_file}` and the curve "
                f"{variable}, `fileNameFilter` ({curve.file_name_filter}) is too"
                "restrictive and does not match any CSV file. ❌",
                fg=colors.BRIGHT_RED,
            )

            raise Exit()

        if trash != []:
            secho(
                "❌ ERROR: ",
                fg=colors.BRIGHT_RED,
                bold=True,
                nl=False,
            )

            secho(
                f"For configuration file `{chosen_configuration_file}` and the curve "
                f"{variable}, `fileNameFilter` ({curve.file_name_filter}) is too "
                "loose and matches multiple CSV files. ❌",
                fg=colors.BRIGHT_RED,
            )

            raise Exit()

        curve.file_path = matching_file

    file_path_to_variables = {
        file_path: {variables for _, variables in file_path_and_variables}
        for file_path, file_path_and_variables in groupby(
            sorted(
                (
                    (curve.file_path, curve.variable)
                    for curve in chosen_configuration.curves
                )
            ),
            lambda x: x[0],
        )
    }

    x = chosen_configuration.general.variable

    for csv_path in csvs_path:
        secho(
            f"Process CSV file {csv_path}... ",
            fg=colors.BRIGHT_GREEN,
            bold=True,
            nl=False,
        )

        pad_and_sample(csv_path, FILES_DIR, x, cpu_count())
        secho("OK", fg=colors.BRIGHT_GREEN, bold=True)

    win = GraphicsLayoutWidget(show=True, title=f"🌊 CSV PLOT 🏄")
    win.showMaximized()

    first_plot: Optional[PlotItem] = None

    def get_plot(layout_item: Configuration.LayoutItem) -> PlotItem:
        plot: PlotItem = win.addPlot(
            row=layout_item.x - 1,
            col=layout_item.y - 1,
            title=layout_item.title,
            axisItems=(
                {"bottom": DateAxisItem()}
                if chosen_configuration.general.as_datetime
                else {}
            ),
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

        return plot

    position_to_plot: Dict[Tuple[int, int], PlotItem] = (
        {
            (layout_item.x, layout_item.y): get_plot(layout_item)
            for layout_item in chosen_configuration.layout
        }
        if chosen_configuration.layout is not None
        else {}
    )

    def compute_low_high(
        curve: Configuration.Curve, position_to_plot: Dict[Tuple[int, int], PlotItem]
    ) -> Tuple[PlotCurveItem, PlotCurveItem]:
        color = COLOR_NAME_TO_HEXA[curve.color]
        low = PlotCurveItem(pen=color)
        high = PlotCurveItem(pen=color)
        fill = FillBetweenItem(low, high, color)

        if not (curve.x, curve.y) in position_to_plot:
            position_to_plot[(curve.x, curve.y)] = get_plot(
                Configuration.LayoutItem(position=f"{curve.x}-{curve.y}")
            )

        plot = position_to_plot[(curve.x, curve.y)]

        plot.addItem(low)
        plot.addItem(high)
        plot.addItem(fill)

        return low, high

    path_variable_to_low_high = {
        (FILES_DIR / pseudo_hash(curve.file_path, x), curve.variable): compute_low_high(
            curve, position_to_plot
        )
        for curve in chosen_configuration.curves
    }

    first_plot, *plots = position_to_plot.values()

    for plot in plots:
        plot.setXLink(first_plot)

    date_time_formats = chosen_configuration.general.date_time_formats

    def date_time_parser(x: str, date_time_formats: List[str]) -> datetime:
        for date_time_format in date_time_formats:
            try:
                return datetime.strptime(x, date_time_format)
            except ValueError:
                pass

        raise ValueError(
            f"time data '{x}' does not match any format in " "{date_time_formats}"
        )

    parser = (
        (lambda x: date_time_parser(x, date_time_formats))
        if date_time_formats is not None
        else float
    )

    connector, background_connector = Pipe()

    background_processor = BackgroundProcessor(
        {
            FILES_DIR / pseudo_hash(file_path, x): variables
            for file_path, variables in file_path_to_variables.items()
        },
        (x, parser),  # type: ignore
        background_connector,
    )

    def on_sig_x_range_changed():
        x_range, _ = first_plot.viewRange()
        x_min, x_max = x_range

        connector.send((x_min, x_max, int(first_plot.width())))

    def update():
        while True:
            item: Optional[
                Tuple[str, List[float], Dict[str, Selected.Y]]
            ] = connector.recv()

            if item is None:
                return

            dir_path, xs, variable_to_y = item

            for variable, y in variable_to_y.items():
                low, high = path_variable_to_low_high[(dir_path, variable)]
                low.setData(xs, y.mins)
                high.setData(xs, y.maxs)

    update_thread = Thread(target=update)
    update_thread.start()

    try:
        first_plot.sigXRangeChanged.connect(on_sig_x_range_changed)
        background_processor.start()
        connector.send((None, None, int(first_plot.width())))

        app = mkQApp()
        app.setWindowIcon(QIcon(str(ICON_PATH)))
        app.exec()
    finally:
        connector.send(None)
        background_processor.join()
