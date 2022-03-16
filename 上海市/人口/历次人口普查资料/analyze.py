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

dfs = msd.load()
df = dfs
fig, axes = plt.subplots(2, 1)
df_65_plus = df['常住人口'].loc[:,'65-69':'80+']
df_15_minus = df['常住人口'].loc[:,'0-4':'10-14']
df_total = df['常住人口','合计']
df_all = pd.DataFrame({'总常住人口数': df_total, '小于15岁': df_15_minus.sum(axis=1), '65岁+' : df_65_plus.sum(axis=1)})
ax = df_all.plot.bar(ax = axes[0], grid = True, title = "上海人口普查常住人口数", ylabel = "人口数")

ax = df_65_plus.plot.bar(ax = axes[1], grid = True, title = '上海老龄人人数', ylabel = '人数')
for container in ax.containers:
    ax.bar_label(container)

df_65_plus_pct = df_65_plus.div(df_total, axis = 'index') * 100
df_65_plus_pct = df_65_plus_pct.sum(axis = 1).apply(lambda x: round(x,1))
ax = ax.twinx()
ax.plot(df_65_plus_pct.index.strftime('%Y'), df_65_plus_pct, color = 'k', linestyle = 'dashed', marker='o')
ax.set_ylabel("65岁以上占百分比（%）")
for i, v in df_65_plus_pct.iteritems():
    if not v:
        continue
    i = i.strftime('%Y')
    ax.text(i, v + 0.2, v)

#df0, df1 = tuple(msd.load(['./', '../一般公共预算收支']))
#df1 = df1.drop(df1.columns[-1], axis = 1)
#cols = pd.MultiIndex.from_arrays([['一般公共预算收入', '一般公共预算收入'], ['税收收入', '非税收入'], ['税收收入', '非税收入']])
#df1.columns = cols
#merged_df = df0.reset_index().merge(df1, how="left").set_index('index')

    