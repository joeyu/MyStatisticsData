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
s_65_plus = df['常住人口'].loc[:,'65-69':].sum(axis=1)
s_15_minus = df['常住人口'].loc[:,'0-4':'10-14'].sum(axis=1)
s_total = df['常住人口','合计']
df_combined = pd.DataFrame({'总常住人口数': s_total, '小于15岁': s_15_minus, '65岁+' : s_65_plus})
df_combined.plot.bar(grid = True, title = "上海历年人口普查常住人口数", ylabel = "人口数")

#df0, df1 = tuple(msd.load(['./', '../一般公共预算收支']))
#df1 = df1.drop(df1.columns[-1], axis = 1)
#cols = pd.MultiIndex.from_arrays([['一般公共预算收入', '一般公共预算收入'], ['税收收入', '非税收入'], ['税收收入', '非税收入']])
#df1.columns = cols
#merged_df = df0.reset_index().merge(df1, how="left").set_index('index')

    