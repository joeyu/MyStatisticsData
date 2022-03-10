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

def load_meta(meta_fp:str):
    with io.open(meta_fp, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return meta

def load(data_fp:str = '.'):
    """
    Loads raw data from all stored .csv files
    """

    meta_fn = 'meta.json'
    fp = Path(data_fp).resolve()
    if fp.is_dir():
        meta_fn = str(fp / meta_fn)
        fp_array = fp.glob('*.csv')
    elif fp.is_file():
        meta_fn = str(fp.parent / meta_fn)
        fp_array = [fp]

    meta = load_meta(meta_fn)

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
        if meta['index_orientation'] == 1:
            df = df.T

        # if meta['index_orientation'] == 0:
        index = df.index
        periods = []
        data = []
        for i in index:
            if 'A-DEC' in meta['index_freq'] or ('Q-DEC' in meta['index_freq'] and meta['accumulated']):
                i = i.strip()
                try:
                    i_dt = datetime.strptime(i, meta['index_formats']['Y'])
                except ValueError:
                    logging.warning(f"Row '{i}' of file '{fpath}' is ignored!")
                    continue
                else:
                    periods.append(pd.Period(i_dt, freq = "A-DEC"))
                    data.append([ii * meta['unit'] for ii in pd.to_numeric(df.loc[i,:])])
                
        if data and periods:
            period_index = pd.PeriodIndex(periods, freq = 'A-DEC')
            df = pd.DataFrame(data, index = period_index, columns = df.columns)

            # Append to the DataFrame array
            df_array.append(df)

    # Combine all the DataFrame array and sort ascendently
    combined_df = pd.concat(df_array)

    return combined_df.sort_index(axis = 0)

def loadm(data_fp):
    df_array = []
    if type(data_fp) == str:
        data_fp = [data_fp]
    for fp in data_fp:
        df = load(fp)
        df_array.append(df)

    return pd.concat(df_array, axis = 1) 

#Set font to support Chinese
mpl.rc('font', family = 'SimHei')

def plot_twinx(df1, df2):
    if isinstance(df1, pd.core.series.Series):
        df1 = pd.DataFrame(df1)

    if isinstance(df2, pd.core.series.Series):
        df2 = pd.DataFrame(df2)

    fig, axes = plt.subplots(len(df1.columns), 1, sharex = True)
    if not isinstance(axes, np.ndarray): 
        axes = [axes]
    for i in range(len(df1.columns)):
        ax = axes[i]
        ax.bar(df1.index.strftime('%Y'), df1.iloc[:,i])
        ax.set_ylabel(df1.columns[i] + "（元）")

        ax0 = ax.twinx()
        ax0.plot(df2.index.strftime('%Y'), df2.iloc[:,i], color = "red")
        ax0.set_ylabel(df2.columns[i])

def plot_with_pct_change(df, title:str = None):
    if isinstance(df, pd.core.series.Series):
        df = pd.DataFrame(df)

    pct = df.pct_change() * 100    
    pct.columns = [s + " Change %" for s in pct]
    plot_twinx(df, pct)

def data_and_pct_change(data):
    pct = data.pct_change()
    pct.name = "Change%"
    return pd.concat([data, pct], axis = 1)

def excel_to_cvs(excel_fp:str, cvs_fp_prefix:str):
    sheet_df_dicts = pd.read_excel(excel_fp, sheet_name=None)

    garbages = r"[  　]";
    for name, df in sheet_df_dicts.items():
        df.columns = [re.sub(garbages, '', s) for s in df]
        df = df.applymap(lambda x: re.sub(garbages, '', x) if type(x) == str else x)
        df.to_csv(f"{cvs_fp_prefix}_{name}.csv", index=False)
