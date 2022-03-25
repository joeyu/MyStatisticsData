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

#fp_array = Path("raw").glob('*.csv')
#for fp in fp_array:
#    d = pd.read_csv(fp, index_col = [0], header=[0])
#    d = d.T * 1E4
#    d.to_csv(fp.name)

dfs = msd.load()
df = dfs
fig, axes = plt.subplots(2, 1)
df_total = df[['总计', '政府性基金收入合计']]
ax = df_total.plot.bar(ax = axes[0], title = '安徽省政府性基金收入', ylabel = "收入（元）", grid = True)
for container in ax.containers:
    ax.bar_label(container)
ax_twinx = ax.twinx()
s_sum_pct = df['政府性基金收入合计'].pct_change() * 100
ax_twinx.plot(s_sum_pct.index.strftime('%Y'), s_sum_pct, linestyle = '--', color = 'r')
ax_twinx.set_ylabel('政府性基金收入年增长率（%）')
for k, v in s_sum_pct.iteritems():
    k = k.strftime('%Y')
    v = round(v, 1)
    ax_twinx.text(k, v + 0.2, v)

df_major_taxes = df[['国有土地使用权出让收入', '地方政府专项债务收入']]
ax = df_major_taxes.plot.bar(ax = axes[1], title = "安徽省政府性基金主要收入", ylabel = "收入（元）", grid = True)
for container in ax.containers:
    ax.bar_label(container)

    