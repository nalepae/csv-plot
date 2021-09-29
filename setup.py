from setuptools import setup, Extension

setup(
    ext_modules=[Extension("fast_pad_and_sample", ["csv_plot/fast_pad_and_sample.c"])]
)
