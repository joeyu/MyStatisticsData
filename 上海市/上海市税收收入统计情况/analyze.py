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

def excel_to_cvs(excel_file):
    sheet_df_dicts = pd.read_excel(excel_file, sheet_name=None)

    for name, df in sheet_df_dicts.items():
        df.columns = [re.sub(r"[  　]",  '', s) for s in df.columns]
        for i in range(len(df)):
            df.iloc[i,0] = re.sub(r"[  　]",  '', df.iloc[i,0])
        df.to_csv(f"上海市税收收入统计情况_{name}.csv", index=False)

def load_raw_data(raw_dir:str):
    """
    Loads raw data from all stored .csv files
    """
    d = Path(raw_dir)
    combind_df = None
    df_array = []
    for fpath in d.glob('**/*.csv'):
        print(fpath)
        df = pd.read_csv(fpath)
        new_col = [s.strip() for s in df.iloc[:,0].values]

        # year data
        data = pd.to_numeric(df.iloc[:,-1])
        data = [data.values]

        # year
        m = re.search(r"[12]\d\d\d", Path(fpath).stem)
        year = m.group()
        index = pd.PeriodIndex([year], freq = 'A-DEC')
        df = pd.DataFrame(data, index = index, columns = new_col)
        df_array.append(df)

    combind_df = pd.concat(df_array)
    return combind_df.sort_index(axis = 0)

def data_and_pct_change(data):
    pct = data.pct_change()
    pct.name = "Change%"
    return pd.concat([data, pct], axis = 1)

combined_df = load_raw_data('raw')

#Set font to support Chinese
mpl.rc('font', family = 'SimHei')

def plot_with_pct_change(df, columns, title:str = None):
    fig, axes = plt.subplots(len(columns), 1, sharex = True)
    if not isinstance(axes, np.ndarray): 
        axes = [axes]
    for i, col in enumerate(columns):
        ax = axes[i]
        ax.bar(df.index.strftime('%Y'), df[col])
        ax.set_ylabel(col + "（万元）")

        pct = df[col].pct_change()
        pct = pct.apply(lambda x: x * 100)
        ax2 = ax.twinx()
        ax2.plot(df.index.strftime('%Y'), pct, color = "red")
        ax2.set_ylabel("Change%")

#combined_df.to_excel("a.xlsx")





    
    

    