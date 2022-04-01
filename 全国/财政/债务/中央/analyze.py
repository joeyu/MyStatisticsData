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
s_liability = df['合计']
fig, axes = plt.subplots(1, 1)
ax = msd.plot_bar(s_liability, ax = axes, title = '中央财政国债余额', ylabel = '账务余额（元）')
    
s_liability_pct = s_liability.pct_change().apply(lambda x: round(100 * x, 1))
msd.plot(s_liability_pct, ax = ax.twinx(), ylabel = '年增长率（%）', linestyle = "--", color = 'r')