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
df_balance = df['合计']
ax = df.plot.bar(title = '上海市政府债务余额', ylabel = '账务余额（元）')
for container in ax.containers:
    ax.bar_label(container)
    
ax = ax.twinx()
df_balance_pct = df_balance.pct_change() * 100
df_balance_pct = df_balance_pct.apply(lambda x: round(x, 1))
ax.plot(df_balance_pct.index.strftime('%Y'), df_balance_pct, linestyle = '--', color = 'r')
ax.set_ylabel("合计年增长率（%）")
for i, v in df_balance_pct.iteritems():
    i = i.strftime('%Y')
    ax.text(i, v + 0.2, v)

    