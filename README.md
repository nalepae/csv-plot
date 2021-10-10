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

## Official documentation

The official documentation is hosted on Github Pages: https://nalepae.github.io/csv-plot

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
