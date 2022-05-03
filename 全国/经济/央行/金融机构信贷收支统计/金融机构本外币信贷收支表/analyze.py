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

renames = {
    '2.企（事）业单位贷款 Loans to Non-financial Enterprises and Government Departments & Organizations': [
        '2.非金融企业及机关团体贷款 Loans to Non-financial Enterprises and Government Departments & Organizations']
}

dfs = [msd.df_rename_columns(x, renames) for x in dfs]


    