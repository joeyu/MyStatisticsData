# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 20:09:49 2022

@author: Zhou Yu
"""
import sys
import re
from more_itertools import combination_index
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from fontTools.ttLib import TTFont
import numpy as np
from pathlib import Path
import io
import json

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

dfs = msd.load()

def convert_raw(raw_fp:str = '.'):
    fp = Path(raw_fp).resolve()
    if fp.is_dir():
        fp_array = fp.glob('*.csv')
    elif fp.is_file():
        fp_array = [fp]

    df_array = []
    for fpath in fp_array:
        print(f"Reading '{fpath}'...")
        df = pd.read_csv(fpath)
        
        stride = 7
        df.iloc[0:stride,1:] = df.iloc[0:stride,1:] * 1E4
        df.iloc[stride:stride*2,1:] = df.iloc[stride:stride*2,1:] * 1E8
        df.iloc[stride*2:,1:] = df.iloc[stride*2:,1:] * 1E4

        df.iloc[3,1:] = df.iloc[1,1:] - df.iloc[2,1:]
        df.iloc[stride+3,1:] = df.iloc[stride+1,1:] - df.iloc[stride+2,1:]
        df.iloc[stride*2+3,1:] = df.iloc[stride*2+1,1:] - df.iloc[stride*2+2,1:]

        df_array.append(df)

    combined_df = pd.concat(df_array, axis = 1)
    return combined_df

#df = convert_raw('raw')