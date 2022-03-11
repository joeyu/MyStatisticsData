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

from sympy import proper_divisor_count

def load_meta(meta_fp:str):
    with io.open(meta_fp, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return meta

def load(data_fp:str = '.'):
    """
    Loads raw data from all stored .csv files
    """
    meta_fn = 'meta.json'

    if type(data_fp) == str:
        data_fp = [data_fp]
    else:
        data_fp = data_fp

    fp_array = []
    for fp in data_fp:
        fp = Path(fp).resolve()
        if fp.is_dir():
            fp_array.extend(fp.glob('*.csv'))
        else:
            fp_array.append(fp)

    df_freq_groups = {}
    for fp in fp_array:
        logging.info(f"Reading '{fp}'...")
        meta_fn = str(fp.parent / meta_fn)
        meta = load_meta(meta_fn)
        header = 0
        if 'header' in meta:
            header = meta['header']
        index_col = 0
        df = pd.read_csv(fp, index_col = index_col, header = header)
        df.index = pd.PeriodIndex([pd.Period(i) for i in df.index])

        freqstr = df.index.freqstr
        if freqstr in df_freq_groups:
            df_freq_groups[freqstr] = pd.concat([df_freq_groups[freqstr], df])
        else:
            df_freq_groups[freqstr] = df

    # Combine all the DataFrame array and sort ascendently
    return [df.sort_index(axis = 0) for df in df_freq_groups.values()]

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
