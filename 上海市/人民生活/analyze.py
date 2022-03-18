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
df_income = df.loc['2000':, '居民人均可支配收入']
df_spending = df.loc['2000':, '居民人均消费支出']
ax = df_income.plot.bar(ax = axes[0], grid = True, title = "上海市居民人均可支配收入", ylabel = "人均可支配收入（元）")
ax.set_ylim(ax.get_ylim()[0], df_income['合计'].max())
for container in ax.containers:
    ax.bar_label(container)
df_income_pct = df_income['合计'].pct_change().apply(lambda x: round(x * 100, 1))
ax = ax.twinx()
ax.plot(df_income_pct.index.strftime('%Y'), df_income_pct)
ax.set_ylabel("年增长（%）")
ax.set_ylim(0, ax.get_ylim()[1])
for k, v in df_income_pct.iteritems():
    k = k.strftime("%Y")
    ax.text(k, v, v)


ax = df_spending.plot.bar(ax = axes[1], grid = True, title = "上海市居民人均消费支出", ylabel = "人均消费支出（元）")
ax.set_ylim(ax.get_ylim()[0], df_income['合计'].max())
for container in ax.containers:
    ax.bar_label(container)
df_spending_pct = df_spending['合计'].pct_change().apply(lambda x: round(x * 100, 1))
ax = ax.twinx()
ax.plot(df_spending_pct.index.strftime('%Y'), df_spending_pct)
ax.set_ylabel("年增长（%）")
lim0, lim1 = ax.get_ylim()
lim0, lim1 = lim0 * 2, lim1 * 2
if lim0 > 0:
    lim0 = 0 
ax.set_ylim(lim0, lim1)
for k, v in df_spending_pct.iteritems():
    k = k.strftime("%Y")
    ax.text(k, v, v)


    