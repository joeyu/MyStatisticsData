# MyStatisticsData
Statistics data for analysis and learning of `pandas`.

## Data file
Data are stored in .cvs files, which can be loaded by `pandas.read_cvs()`.

Index must be `pandas.Period` as string, and all indices of a file shall have same `freq`.

A .cvs file has meta data for loading, which is stored in file 'meta.json' in the same directory. All of the .cvs files of the same directory share one same 'meta.json' file.

## [`MyStatisticsData`](./MyStatisticsData.py)
Module `MyStatisticsData` provides all helper routines that can be used to load, process and store the data.
