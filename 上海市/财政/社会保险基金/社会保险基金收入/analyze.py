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

fp_array = Path("raw").glob('*.csv')
for fp in fp_array:
    d = pd.read_csv(fp, index_col = [0], header=[0])
    d = d.T * 1E8
    d.to_csv(fp.name)

dfs = msd.load()
df = dfs
fig, axes = plt.subplots(2, 1)
df_total = df[['社会保险基金收入合计', '中央调剂资金收入']]
ax = df_total.plot.bar(ax = axes[0], title = '上海社保收入', ylabel = "收入（元）", grid = True)
for container in ax.containers:
    ax.bar_label(container)
ax_twinx = ax.twinx()
s_income = df['社会保险基金收入合计']
s_income_pct = s_income.pct_change() * 100
ax_twinx.plot(s_income_pct.index.strftime('%Y'), s_income_pct, linestyle = '--', color = 'r')
for k, v in s_income_pct.iteritems():
    v = round(v, 2)
    k = k.strftime('%Y')
    ax_twinx.text(k, v + 0.1, v)
ax_twinx.set_ylabel("年增长百分比（%）")

df_indiv = df[['企业职工基本养老保险基金收入','机关事业单位基本养老保险基金收入', '职工基本医疗保险基金收入']]
ax = df_indiv.plot.bar(ax = axes[1], title = "上海社保收入（分项）", ylabel = "收入（元）", grid = True)
for container in ax.containers:
    ax.bar_label(container)

#fig, axes = plt.subplots(1, 1)
#s_ratio = df['企业职工基本养老保险基金收入'] / df['机关事业单位基本养老保险基金收入']
#ax = s_ratio.plot(title = '企业职工和机关事业单位基本养老保险基金收入之比')
#for k, v in s_ratio.iteritems():
#    v = round(v, 2)
#    k = k.strftime('%Y')
#    ax.text(k, v + 0.1, v)


    