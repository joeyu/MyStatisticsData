import logging
import re
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from fontTools.ttLib import TTFont
import numpy as np
from pathlib import Path
import io
import json
from datetime import datetime

from sympy import per

def load_meta(meta_fp:str = 'meta.json'):
    with io.open(meta_fp, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return meta

def load_raw(raw_fp:str = '.', meta_fn:str = 'meta.json'):
    """
    Loads raw data from all stored .csv files
    """

    meta = load_meta(meta_fn)
    meta_raw = meta['raw']
    #print(meta_raw)
    fp = Path(raw_fp)
    if fp.is_dir():
        fp_array = fp.glob('**/*.csv')
    elif fp.is_file():
        fp_array = [fp]

    combined_df = None
    df_array = []
    for fpath in fp_array:
        # if not '2021' in fpath.name:
        #    continue 
        logging.info(f"Reading '{fpath}'...")
        df = pd.read_csv(fpath)

        # Set column 0 as index
        df = df.set_index(df.columns[0])

        # transpose the df
        if meta_raw['index_orientation'] == 1:
            df = df.T

        # if meta_raw['index_orientation'] == 0:
        index = df.index
        periods = []
        data = []
        for i in index:
            if 'year' in meta_raw['index_freq']:
                i = i.strip()
                try:
                    i_dt = datetime.strptime(i, meta_raw['indices']['Y'])
                except ValueError:
                    logging.warning(f"Row '{i}' of file '{fpath}' is ignored!")
                    continue
                else:
                    periods.append(pd.Period(i_dt, freq = "A-DEC"))
                    row_data = [ii * meta_raw['unit'] for ii in pd.to_numeric(df.loc[i,:])]
                    data.append(row_data)
                
        if data and periods:
            period_index = pd.PeriodIndex(periods, freq = 'A-DEC')
            df = pd.DataFrame(data, index = period_index, columns = df.columns)

            # Append to the DataFrame array
            df_array.append(df)

    # Combine all the DataFrame array and sort ascendently
    combined_df = pd.concat(df_array)

    return combined_df.sort_index(axis = 0)

#Set font to support Chinese
mpl.rc('font', family = 'SimHei')

def plot_with_pct_change(df, title:str = None):
    if isinstance(df, pd.core.series.Series):
        df = pd.DataFrame(df)

    pct = df.pct_change() * 100    
    fig, axes = plt.subplots(len(df.columns), 1, sharex = True)
    if not isinstance(axes, np.ndarray): 
        axes = [axes]
    for i, col in enumerate(df.columns):
        ax = axes[i]
        ax.bar(df.index.strftime('%Y'), df[col])
        ax.set_ylabel(col + "（元）")

        ax0 = ax.twinx()
        ax0.plot(df.index.strftime('%Y'), pct[col], color = "red")
        ax0.set_ylabel("Change%")

def data_and_pct_change(data):
    pct = data.pct_change()
    pct.name = "Change%"
    return pd.concat([data, pct], axis = 1)
