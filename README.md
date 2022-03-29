# MyStatisticsData
Statistics data for analysis of economy and learning of `pandas`.

## Data file
Data are stored in .csv files, which can be loaded by `pandas.read_csv()`.

Index must be `pandas.Period` as string, and all indices of a file shall be of same `freq`.

A .csv file has meta data for loading, which is stored in file 'meta.json' in the same directory. All of the .csv files of the same directory share one same 'meta.json' file.

## [`MyStatisticsData`](./MyStatisticsData.py)
Module `MyStatisticsData` provides all helper routines that can be used to load, process and store the data.
