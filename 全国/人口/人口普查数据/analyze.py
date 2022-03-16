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
from sqlalchemy import column

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

dfs = msd.load()
df = dfs
cities = df.columns.levels[0].drop('全国')
df_cities = pd.DataFrame()
df_pct_cities = pd.DataFrame()
for ci in cities:
    cnt_total = df[ci, '性别合计', '年龄合计']
    cnt_15_minus = df[ci, '性别合计'].loc[:,'0-4':'10-14'].sum(axis=1)
    cnt_15_64 = df[ci, '性别合计'].loc[:,'15-19':'60-64'].sum(axis=1)
    cnt_65_plus = df[ci, '性别合计'].loc[:,'65-69':'100+'].sum(axis=1)
    df_ci = pd.DataFrame({'<=15岁': cnt_15_minus, '15-64岁': cnt_15_64, '>=65岁': cnt_65_plus})
    df_ci.index = [ci]
    df_cities = pd.concat([df_cities, df_ci], axis = 0)
    df_ci_pct = pd.DataFrame({'<=15岁': cnt_15_minus / cnt_total, '15-64岁': cnt_15_64 / cnt_total, '>=65岁': cnt_65_plus / cnt_total}) * 100
    df_ci_pct.index = [ci]
    df_pct_cities = pd.concat([df_pct_cities, df_ci_pct], axis = 0)

fig, axes = plt.subplots(2, 1, sharex = True)
ax = df_cities.plot.bar(ax = axes[0], title = "2010年第六次人口普查数据（分地区）年龄分布", ylabel = "人口数")
df_pct_cities.plot.bar(ax = axes[1], title = "2010年第六次人口普查数据（分地区）年龄分布比分比", ylabel = "占总人数%")


#df0, df1 = tuple(msd.load(['./', '../一般公共预算收支']))
#df1 = df1.drop(df1.columns[-1], axis = 1)
#cols = pd.MultiIndex.from_arrays([['一般公共预算收入', '一般公共预算收入'], ['税收收入', '非税收入'], ['税收收入', '非税收入']])
#df1.columns = cols
#merged_df = df0.reset_index().merge(df1, how="left").set_index('index')

    