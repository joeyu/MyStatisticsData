# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 20:09:49 2022

@author: Zhou Yu
"""
import logging
import sys
import re
from importlib_metadata import always_iterable
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
df_liability = df
df_balance = df[['上海市', '深圳市', '重庆市', '广东省', '江苏省', '安徽省']]
fig, axes = plt.subplots(2, 1)
ax = msd.plot_bar(df_balance, ax = axes[0], title = '地方政府债务余额（代表地区）', ylabel = '账务余额（元）')
    
df_balance = df_balance.drop('深圳市', axis = 1)
df_balance_pct = df_balance.pct_change().apply(lambda x: round(100 * x, 1))
df_balance_pct.plot(ax = axes[1], grid = True, title = '地方政府债务余额年增长率（代表地区）', ylabel = '年增长率（%）')

fig, ax = plt.subplots(1, 1)
df_gpbr = msd.load('../../一般公共预算收入/地方一般公共预算收入/')
df_gf = msd.load('../../政府性基金收入/地方政府性基金收入/')
df_cc = (df_liability / ( df_gpbr + df_gf)).applymap(lambda x: round(x, 2))
ax = msd.plot_bar(df_cc.loc[['2018', '2019', '2020']].T, ax = ax, title = '2018/2019/2020年地方政府偿债能力 —— 债务余额 / (一般公共预算收入 + 政府性基金收入)')

fig, axes = plt.subplots(2, 1)
s_liability_sum = df_liability.sum(axis = 1)
s_liability_sum_pct = s_liability_sum.pct_change().apply(lambda x: round(100 * x, 1))
ax = msd.plot_bar(s_liability_sum, ax = axes[0], title = '地方政府债务余额合计', ylabel = '债务余额（元）')
msd.plot(s_liability_sum_pct, ax = ax.twinx(), ylabel = "年增长率（%）", linestyle = "--", color = 'r')

s_gpbr_sum = df_gpbr.sum(axis = 1)
s_gf_sum = df_gf.sum(axis = 1)
s_cc_sum = (s_liability_sum / (s_gpbr_sum + s_gf_sum)).apply(lambda x: round(x, 2))
s_cc_sum_pct = s_cc_sum.pct_change().apply(lambda x: round(100 * x, 1))
ax = msd.plot_bar(s_cc_sum, ax = axes[1], title = "地方政府偿债能力 —— 债务余额合计 / (一般公共预算收入合计 + 政府性基金收入合计)")
msd.plot(s_cc_sum_pct, ax = ax.twinx(), ylabel = "年增长率（%）", linestyle = '--', color = 'r')
