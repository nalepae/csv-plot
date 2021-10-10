<div align="center">
  <img src="https://raw.githubusercontent.com/nalepae/csv-plot/master/csv_plot/assets/icon-256.png"><br>
</div>

---

# CSV Plot: easy and powerful plotting tool for CSV files

[![PyPI Latest Release](https://img.shields.io/pypi/v/csv-plot.svg)](https://pypi.org/project/csv-plot/)
[![License](https://img.shields.io/pypi/l/pandas.svg)](https://github.com/pandas-dev/pandas/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## What is it?

**CSV Plot** is a tool to easily plot any CSV file, of any size, without never getting out of memory errors.
(Only data which is displayed on the screen is loaded into memory.)

It works with user friendly YAML configuration files, to let you choose the layout, colors, units, legends...

**CSV Plot** is built on top of the amazing [PyQtGraph](https://www.pyqtgraph.org/) library, which ensures a nice and smooth experience, as plotting should always be.

## Installation

A already installed C compiler is needed to install `csv-plot`, else the installation
will fail. To know how to install a C compiler on your system, go to [Installing a C
compiler](##installing-a-c-compiler) section at the end of this document.

```bash
$ pip install csv-plot
```

## Complete tutorial

### Introduction

**CSV Plot** is based on two main elements:

- A CSV file (contains _what_ you want to plot)
- A configuration file (contains _how_ do you want to plot it)

### The simplest possible example

#### Here we go

Download the file [example_file.csv](https://raw.githubusercontent.com/nalepae/csv-plot/master/docs/example_file.csv).

This CSV file contains 1.000 rows of 5 columns:

- `index`
- `sin`
- `cos`
- `sin_rand`
- `cos_rand`

Copy the following content if a file called `configuration-1.yaml`.

```yaml
general:
  variable: index

curves:
  - variable: sin
```

⚠️ Don't forget the `-` in the `curves` section. We'll explain why it's needed after. ⚠️

Then write

```bash
$ csv-plot <path-to-csv-file> -c <path-to-configuration-1.yaml>
```

Here we are, you get your first shiny plot!

- To move, keep left mouse button pressed then move the mouse.
- To zoom:
  - keep right mouse button pressed then move the mouse, or
  - use the middle mouse wheel.
- To reset, click on the `A` button on the bottom left of the window.

You can also right click to discover all the available options.

You can type

```bash
$ csv-plot --help
```

to get help on the available options.

#### Explanation of the configuration file

- The `general/variable` value indicates which column is used as abscissa (here `index`)
- The `curve/variable` value indicates which column is used as ordinate (here `sin`)

### Two curves on the same plot

#### Here we go

Copy the following content if a file called `configuration-2.yaml`.

```yaml
general:
  variable: index

curves:
  - variable: sin

  - variable: cos
    color: green
```

Then write

```bash
$ csv-plot <path-to-csv-file> -c <path-to-configuration-2.yaml>
```

#### Explanation of the configuration file

You see two curves. `sin` is in yellow, `cos` is in green. If no color is specified,
**CSV Plot** defaults to yellow.

Here is the list of available colors: `aqua`, `black`, `blue`, `fuchsia`, `gray`,
`green`, `lime`, `maroon`, `navy`, `olive`, `orange`, `purple`, `red`, `silver`, `teal`,
`white` & `yellow`.

### Multiple sub plots

#### Here we go

Copy the following content if a file called `configuration-3.yaml`.

```yaml
general:
  variable: index

curves:
  - variable: sin
    position: 1-1

  - variable: cos
    position: 1-1
    color: green

  - variable: sin_rand
    position: 2-1
    color: purple

  - variable: cos_rand
    position: 2-1
    color: aqua
```

Then write

```bash
$ csv-plot <path-to-csv-file> -c <path-to-configuration-1.yaml>
```

#### Explanation of the configuration file

You see 4 curves. Additionally to the previous example, we added for each curve the
`position` item. This item is composed of `<number>-<number>`.

- The first `number` represents the row of the subplot.
- The second `number` represents the column of the subplot.

### Adding titles, labels and units

#### Here we go

Copy the following content if a file called `configuration-4.yaml`.

```yaml
general:
  variable: index
  label: Time
  unit: sec

curves:
  - variable: sin
    position: 1-1

  - variable: cos
    position: 1-1
    color: green

  - variable: sin_rand
    position: 2-1
    color: purple

  - variable: cos_rand
    position: 2-1
    color: aqua

layout:
  - position: 1-1
    title: Waves
    label: Height
    unit: m

  - position: 2-1
    title: Waves with some randomness
    label: Height
    unit: m
```

Then write

```bash
$ csv-plot <path-to-csv-file> -c <path-to-configuration-4.yaml>
```

#### Explanation of the configuration file

We just added `general/label` and `general/unit`. These 2 values add label/unit of the
`x` axis (bottom of plots)

We also added the `layout` section.
For each sub-plot:

- `position` indicates the position of the sub-plot.
- `label` and `unit` adds label/unit of the `y` axis of the subplot (left of sub-plot)
- `title` adds a title for the sub-plot (top of sub-plot)

## Installing a C compiler

### On Ubuntu

```bash
$ sudo apt update && sudo apt install build-essential
```

### On Mac OS

- Install [homebrew](https://brew.sh/) if not already done

```bash
$ brew install gcc
```

### On Windows

- [Let me Google that for you](https://letmegooglethat.com/?q=Install+GCC+on+windows)
