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
    d = d.T * 1E4
    d.to_csv(fp.name)

dfs = msd.load()
df = dfs
fig, axes = plt.subplots(3, 1)
df_total = df[['总计', '一般公共预算收入合计']]
ax = df_total.plot.bar(ax = axes[0], title = '安徽省一般公共预算收入', ylabel = "收入（元）", grid = True)
for container in ax.containers:
    ax.bar_label(container)
ax_twinx = ax.twinx()
s_sum_pct = df['一般公共预算收入合计'].pct_change() * 100
ax_twinx.plot(s_sum_pct.index.strftime('%Y'), s_sum_pct, linestyle = '--', color = 'r')
ax_twinx.set_ylabel('一般公共预算收入年增长率（%）')
for k, v in s_sum_pct.iteritems():
    k = k.strftime('%Y')
    v = round(v, 1)
    ax_twinx.text(k, v + 0.2, v)

major_taxes = ['个人所得税', '企业所得税', '增值税', '契税', '土地增值税']
df_major_taxes = df[major_taxes]
df_major_taxes.plot.bar(ax = axes[1], title = "安徽省主要税收收入", ylabel = "收入（元）", grid = True)

df_major_subsidies = df[['地方政府一般债务收入','中央税收返还收入', '中央专项转移支付收入', '中央一般性转移支付收入']]
df_major_subsidies.plot.bar(ax = axes[2], title = "债务、中央税收返还及转移支付", ylabel = "收入（元）", grid = True)
    