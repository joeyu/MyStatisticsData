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

df = msd.load()
df_house = df['商品房销售面积', '住宅', '合计']

fig, axes = plt.subplots(2, 1, sharex = True)
# axes[0].bar(df_house.index.strftime("%Y"), df_house, title = "上海住宅销售面积", ylabel = "面积（平米）")
axes[0].bar(df_house.index.strftime("%Y"), df_house)
axes[0].set_title("上海住宅销售面积")
axes[0].set_ylabel("面积（平米）")
axes[0].bar_label(axes[0].containers[0])

df_house_pct = df_house.pct_change() * 100
ax_twinx = axes[0].twinx()
ax_twinx.plot(df_house_pct.index.strftime("%Y"), df_house_pct, color = "r")
ax_twinx.set_ylabel("年增长率（%）")

# area per capita
df_pop = msd.load("../../人口/人口.csv")
row2021 = df_pop.loc['2020'].to_frame()
row2021.columns = pd.PeriodIndex(['2021'], freq='A')
row2021 = row2021.T
df_pop = pd.concat([df_pop, row2021])
df_pop = df_pop.loc[df_house.index,'常住人口']['常住人口']
df_apc = df_house.cumsum() / df_pop
axes[1].bar(df_apc.index.strftime("%Y"), df_apc)
axes[1].set_title("累计住宅销售面积分摊到常住人口（平米/人）")
axes[1].set_ylabel("面积（平米）")
axes[1].bar_label(axes[1].containers[0])

df_apc_pct = df_apc.pct_change() * 100
ax_twinx = axes[1].twinx()
ax_twinx.plot(df_apc_pct.index.strftime("%Y"), df_apc_pct, color = "r")
ax_twinx.set_ylabel("年增长率（%）")

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