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
df_total = df['社会保险基金收入合计']
#df_total.columns = df_total.columns.droplevel()
ax = msd.plot_bar(df_total, ax = axes[0], title = '上海社保收入', ylabel = "收入（元）", grid = True)
s_income = df_total['社会保险基金收入合计']
s_income_pct = s_income.pct_change().apply(lambda x: round(100 * x, 1))
msd.plot(s_income_pct, ax = ax.twinx(), ylabel = "年增长百分比（%）", linestyle = '--', color = 'r')

df_subsidy = df['中央调剂资金收入']
s = df.groupby(level = 1, axis = 1).sum()['财政补贴收入']
s.name = '地方财政补贴收入'
df_subsidy = pd.concat([df_subsidy, s], axis = 1)
ax = msd.plot_bar(df_subsidy, ax = axes[1], title = "财政补贴合计", ylabel = "财政补贴合计（元）", grid = True)
#s_subsidy_pct = s_subsidy.pct_change().apply(lambda x: round(100 * x, 1))
#msd.plot(s_subsidy_pct, ax = ax.twinx(), ylabel = "年增长百分比（%）", linestyle = '--', color = 'r')

#fig, axes = plt.subplots(1, 1)
#s_ratio = df['企业职工基本养老保险基金收入'] / df['机关事业单位基本养老保险基金收入']
#ax = s_ratio.plot(title = '企业职工和机关事业单位基本养老保险基金收入之比')
#for k, v in s_ratio.iteritems():
#    v = round(v, 2)
#    k = k.strftime('%Y')
#    ax.text(k, v + 0.1, v)


    