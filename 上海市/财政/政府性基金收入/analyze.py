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
fig, axes = plt.subplots(1, 1)
df_total = df[['总计', '国有土地使用权出让收入']]
ax = df_total.plot.bar(title = '上海政府性基金收入', ylabel = "收入（元）", grid = True)
for container in ax.containers:
    ax.bar_label(container)
ax_twinx = ax.twinx()

#major_taxes = ['个人所得税', '企业所得税', '增值税', '契税']
#df_major_taxes = df[major_taxes]
#df_major_taxes.plot.bar(ax = axes[1], title = "上海主要税收收入", ylabel = "收入（元）", grid = True)

#fp_array = Path("raw").glob('*.csv')
#for fp in fp_array:
#    d = pd.read_csv(fp, index_col = [0], header=[0])
#    d = d.T * 1E8
#    d.to_csv(fp.name)

    