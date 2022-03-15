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

#df = msd.load(['上海市税收收入统计情况_2021年.csv', '上海市税收收入统计情况_2005年.csv'])
dfs = msd.load()
df_old = dfs['包括外籍家庭佣工', '总计'].loc[:,'65-69':'100+']
df_total = dfs['包括外籍家庭佣工', '总计', '总计']
df_old_pct = df_old.div(df_total, axis = 'index') * 100
ax = df_old_pct.plot.area(grid = True, title = '香港老龄人口数百分比', ylabel = '百分比')
# ax.set_ylabel("百分比%")
# plt.show()

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

    
     

    


    