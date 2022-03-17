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

fig, axes = plt.subplots(2, 1)
# axes[0].bar(df_house.index.strftime("%Y"), df_house, title = "上海住宅销售面积", ylabel = "面积（平米）")
axes[0].bar(df_house.index.strftime("%Y"), df_house)
axes[0].set_title("上海住宅销售面积")
axes[0].set_ylabel("面积（平米）")
axes[0].bar_label(axes[0].containers[0])

df_house_pct = df_house.pct_change() * 100
ax_twinx = axes[0].twinx()
ax_twinx.plot(df_house_pct.index.strftime("%Y"), df_house_pct, color = "r", linestyle="--")
ax_twinx.set_ylabel("年增长率（%）")

# area per capita
df_pop = msd.load("../../人口/人口.csv")
index = df_pop.index
index = index.append(pd.PeriodIndex(['2021'], freq='A'))
df_pop = df_pop.reindex(index, method = 'nearest')

df_pop = df_pop.loc[df_house.index,'常住人口']['常住人口']
df_house_cumsum = df_house.cumsum()
ax = axes[1]
ax.bar(df_house_cumsum.index.strftime("%Y"), df_house_cumsum)
ax.set_title("累计住宅销售面积，以及常住人口人均面积")
ax.set_ylabel("人均面积（平米/人）")
ax.bar_label(axes[1].containers[0])
ax.set_ylim(ax.get_ylim()[0], df_house_cumsum.max() * 2)

#df_apc_pct = df_apc.pct_change() * 100
df_apc = (df_house_cumsum / df_pop).round(1)
ax_twinx = axes[1].twinx()
ax_twinx.plot(df_apc.index.strftime("%Y"), df_apc, color = "r", linestyle="--", marker = 'o')
ax_twinx.set_ylabel("常住人口人均面积（平米/人）")
for k, v in df_apc.iteritems():
    k = k.strftime('%Y')
    ax_twinx.text(k, v+0.4, v)

fig.show()

#df = convert_raw('raw')