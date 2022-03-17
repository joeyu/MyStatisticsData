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
fig, axes = plt.subplots(2, 1)
df_14_minus = dfs['包括外籍家庭佣工', '男女合计'].loc[:,'0-4':'10-14'].sum(axis = 1)
df_15_64 = dfs['包括外籍家庭佣工', '男女合计'].loc[:,'15-19':'60-64'].sum(axis = 1)
df_65_plus = dfs['包括外籍家庭佣工', '男女合计'].loc[:,'65-69':'100+']
df_all = pd.DataFrame({'<15岁': df_14_minus, '15-64岁': df_15_64, '65+岁': df_65_plus.sum(axis=1)})
ax = df_all.plot.bar(ax = axes[0], grid = True, title = '香港老龄人口数百分比', ylabel = '百分比')

df_total = dfs['包括外籍家庭佣工', '男女合计', '年龄合计']
ax = df_65_plus.plot.bar(ax = axes[1], grid = True, title = '香港老龄人人数', ylabel = '人数')
for container in ax.containers:
    ax.bar_label(container)

df_65_plus_pct = df_65_plus.div(df_total, axis = 'index') * 100
df_65_plus_pct = df_65_plus_pct.sum(axis = 1).apply(lambda x: round(x, 1))
ax = ax.twinx()
ax.plot(df_65_plus_pct.index.strftime('%Y'), df_65_plus_pct, color = 'k', linestyle = 'dashed', marker='o')
ax.set_ylabel("65岁以上占百分比（%）")
for i, v in df_65_plus_pct.iteritems():
    if not v:
        continue
    i = i.strftime('%Y')
    ax.text(i, v + 0.2, v)





#df = pd.read_csv("raw/D5211101C2011XXXXC.csv", index_col = [0, 1], header = [0])
#dd = pd.DataFrame()
#for i in df.index.levels[0]:
#    d = pd.DataFrame()
#    # print(i)
#    for j in range(0, 100, 5):
#        # print(j)
#        # print(df.loc[i].loc[str(j): str(j+4)]) 
#        s = df.loc[i].loc[str(j):str(j+4)].sum()
#        #print(s)
#        d[str(j) + '-' + str(j+4)] = s
#    d['100+'] = df.loc[i, '100+']
#    d['总计'] = df.loc[i, '总计']
#    d.columns = pd.MultiIndex.from_arrays([[i] * len(d.columns), d.columns], names =['性别', '年龄段'])
#    dd = pd.concat([dd, d], axis = 1)
#
## levels = [['包括外籍家庭佣工']] + dd.columns.levels
#levels = [['包括外籍家庭佣工'] * len(dd.columns), dd.columns.get_level_values(0).to_list(), dd.columns.get_level_values(1).to_list()]
#dd.columns = pd.MultiIndex.from_arrays(levels, names = ['', '性别', '年龄段'])
## print(dd)

    
     

    


    