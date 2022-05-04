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

dfs = msd.load(merge = False)

dfs = [msd.df_rename_duplicated_columns(x) for x in dfs]

# renames = {
#     '2.企（事）业单位贷款 Loans to Non-financial Enterprises and Government Departments & Organizations': [
#         '2.非金融企业及机关团体贷款 Loans to Non-financial Enterprises and Government Departments & Organizations']
# }

# dfs = [msd.df_rename_columns(x, renames) for x in dfs]

df = pd.concat(dfs).dropna()

fig, axes = plt.subplots(2, 1)

df_i = df[['非金融企业境内股票 Equity financing on the domestic stock market by non-financial enterprises', 
           '企业债券 Net financing of corporate bonds', '政府债券 Government bonds']]
df_i.plot(ax = axes[0], title = '社会融资规模存量', grid = True)
df_i.pct_change(12).plot(ax = axes[1], title = '社会融资规模年增长率', grid = True)
    