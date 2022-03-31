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
df_balance = df[['上海市', '深圳市', '重庆市', '广东省', '江苏省', '安徽省']]
fig, axes = plt.subplots(2, 1)
ax = df_balance.plot.bar(ax = axes[0], title = '地方政府一般公共预算收入', ylabel = '账务余额（元）')
for container in ax.containers:
    ax.bar_label(container)
    
#ax = ax.twinx()
#df_balance = df_balance.drop('深圳市', axis = 1)
df_balance_pct = df_balance.pct_change() * 100
df_balance_pct = df_balance_pct.apply(lambda x: round(x, 1))
df_balance_pct.plot(ax = axes[1], grid = True, title = '地方政府一般公共预算收入年增长率', ylabel = '年增长率（%）')
#ax.set_ylabel("年增长率（%）")
#for i, v in df_balance_pct.iteritems():
#    i = i.strftime('%Y')
#    ax.text(i, v + 0.2, v)

    