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
df_income = df[["地方本级收入", "中央对地方转移支付"]]
ax = msd.plot_bar(df_income, ax = axes[0], title = "地方政府性基金收入", ylabel = "收入（元）")
ax_twinx = ax.twinx()
df_income_pct = df_income.pct_change().applymap(lambda x: round(100 * x, 1))
msd.plot(df_income_pct, ax = axes[1], ylabel = "年增长（%）", linestyle = '--')