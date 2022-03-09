# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 20:09:49 2022

@author: Zhou Yu
"""
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

def excel_to_cvs(excel_fp:str, cvs_fp_prefix:str):
    sheet_df_dicts = pd.read_excel(excel_fp, sheet_name=None)

    for name, df in sheet_df_dicts.items():
        df.columns = [re.sub(r"[  　]",  '', s) for s in df.columns]
        for i in range(len(df)):
            df.iloc[i,0] = re.sub(r"[  　]",  '', df.iloc[i,0])
        df.to_csv(f"{cvs_fp_prefix}_{name}.csv", index=False)

def load_meta(meta_fp:str):
    with io.open(meta_fp, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return meta

def load_raw(raw_dir:str, meta):
    """
    Loads raw data from all stored .csv files
    """
    meta_raw = meta['raw']
    #print(meta_raw)
    d = Path(raw_dir)
    conbined_df = None
    df_array = []
    for fpath in d.glob('**/*.csv'):
        # if not '2021' in fpath.name:
        #    continue 
        print(fpath)
        df = pd.read_csv(fpath)
        if meta_raw['index_orientation'] == 1:
            # column
            new_col = [s.strip() for s in df.iloc[:,0]]

            data = []
            periods = []
            # row
            if 'year' in meta_raw['index_freq']:
                col_regex = '^' + meta_raw['columns']['Y'] + '$'
                col_regex = col_regex.replace('%Y', r'([12]\d{3})')
                for col in df:
                    m = re.match(col_regex, col) 
                    if m:
                        row_data = [i * meta_raw['unit'] for i in pd.to_numeric(df[col]).values]
                        data.append(row_data)
                        periods.append(m.groups()[0])
                        
            # Construct the DataFrame
            if data and periods:
                index = pd.PeriodIndex(periods, freq = 'A-DEC')
                df = pd.DataFrame(data, index = index, columns = new_col)

                # Append to the DataFrame array
                df_array.append(df)

    # Combine all the DataFrame array and sort ascendently
    conbined_df = pd.concat(df_array)

    return conbined_df.sort_index(axis = 0)

def data_and_pct_change(data):
    pct = data.pct_change()
    pct.name = "Change%"
    return pd.concat([data, pct], axis = 1)


meta = load_meta('meta.json')
combined_df = load_raw('raw', meta)

#Set font to support Chinese
mpl.rc('font', family = 'SimHei')

def plot_with_pct_change(df, title:str = None):

    if isinstance(df, pd.core.series.Series):
        df = pd.DataFrame(df)
        
    fig, axes = plt.subplots(len(df.columns), 1, sharex = True)
    if not isinstance(axes, np.ndarray): 
        axes = [axes]
    for i, col in enumerate(df.columns):
        ax = axes[i]
        ax.bar(df.index.strftime('%Y'), df[col])
        ax.set_ylabel(col + "（万元）")

        pct = df[col].pct_change()
        pct = pct.apply(lambda x: x * 100)
        ax2 = ax.twinx()
        ax2.plot(df.index.strftime('%Y'), pct, color = "red")
        ax2.set_ylabel("Change%")

#combined_df.to_excel("a.xlsx")





    
    

    