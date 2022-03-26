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
df_cities = df[['上海市', '深圳市', '重庆市', '广东省', '江苏省', '安徽省']]
fig, axes = plt.subplots(2, 1)
ax = msd.plot_bar(df_cities, ax = axes[0], title = '地方GDP（代表地区）', ylabel = 'GDP（元）')
    
df_cities_pct = df_cities.pct_change().applymap(lambda x: round(100 * x, 1))
df_cities_pct.plot(ax = axes[1], grid = True, title = '地方GDP年增长率（代表地区）', ylabel = '年增长率（%）')

    