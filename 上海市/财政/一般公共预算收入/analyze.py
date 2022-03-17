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
major_taxes = ['个人所得税', '企业所得税', '增值税', '房产税', '契税', '证券交易印花税']
df_major_taxes = df['一般公共预算收入', '税收收入'].loc[:,major_taxes]
df_major_taxes.plot.bar(title = "上海历年主要税收收入", ylabel = "收入（元）")
# df0, df1 = tuple(msd.load(['./', '../一般公共预算收支']))
# df1 = df1.drop(df1.columns[-1], axis = 1)
# cols = pd.MultiIndex.from_arrays([['一般公共预算收入', '一般公共预算收入'], ['税收收入', '非税收入'], ['税收收入', '非税收入']])
# df1.columns = cols
# merged_df = df0.reset_index().merge(df1, how="left").set_index('index')

    