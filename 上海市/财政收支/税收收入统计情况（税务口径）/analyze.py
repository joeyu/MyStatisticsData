# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 20:09:49 2022

@author: Zhou Yu
"""
import logging
import sys
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

from sympy import elliptic_f

module_fn = 'MyStatisticsData.py'
d = Path().cwd()
while True:
    p = d / module_fn
    if p.exists():
        break
    else:
        if d.parent.name == d.name:
            raise FileNotFoundError(f"Can NOT find '{module_fn}'")
        d = d.parent
sys.path.append(str(d))
import MyStatisticsData as msd

#df = msd.load(['上海市税收收入统计情况_2021年.csv', '上海市税收收入统计情况_2005年.csv'])
dfs = msd.load()

def convert_raw(raw_fp:str = '.'):
    fp = Path(raw_fp).resolve()
    if fp.is_dir():
        fp_array = fp.glob('*.csv')
    elif fp.is_file():
        fp_array = [fp]

    pd_array = []
    for fpath in fp_array:
        print(f"Reading '{fpath}'...")
        df = pd.read_csv(fpath, index_col = 0)
        df = df.T
        for i in range(len(df) - 1, 0, -1):
            df.iloc[i,:] = df.iloc[i,:] - df.iloc[i-1,:]
        
        m = re.match(r'[12]\d{3}', df.index[-1])
        y = m.group()

        if len(df) == 1:
            index = [y]
            freq = 'A-DEC'
        elif len(df) == 4:
            index = [y + 'Q' + str(i+1) for i in range(len(df))]
            freq = 'Q-DEC'

        df.index = pd.PeriodIndex(index, freq = freq)
        pd_array.append(df)

        df.to_csv(fpath.name)

    combined_df = pd.concat(pd_array, axis = 0)
    return combined_df

def convert_raw2(raw_fp:str = '.'):
    fp = Path(raw_fp).resolve()
    if fp.is_dir():
        fp_array = fp.glob('*.csv')
    elif fp.is_file():
        fp_array = [fp]

    pd_array = []
    for fpath in fp_array:
        print(f"Reading '{fpath}'...")
        df = pd.read_csv(fpath, index_col = 0)
        df = df.iloc[:,1:]
        cols = df.columns.tolist()
        cols[-1] = '出口退税' 
        cols = [['税收收入合计'] * (len(cols) - 1) + [cols[-1]], cols]
        cols = pd.MultiIndex.from_arrays(cols)
        df.columns = cols
        df = df * 1E4
        #pd_array.append(df)
        df.to_csv(fpath.name)


#convert_raw2()


    