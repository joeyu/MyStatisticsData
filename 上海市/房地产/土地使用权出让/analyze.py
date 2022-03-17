# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 20:09:49 2022

@author: Zhou Yu
"""
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
df_house_commerce = df['出让面积'].loc[:,['住宅', '商业服务']]
df_house_commerce.plot.bar(title = '上海市历年住宅和商业土地出让面积', ylabel = '出让面积（平米）')

#df_house = df['居住房屋'].iloc[:,1:]
#
#fig, axes = plt.subplots(2, 1, sharex = True)
#df_house.plot.bar(ax = axes[0], stacked = True)
#axes[0].set_title("上海居住房屋面积")
#axes[0].set_ylabel("面积（平米）")
#axes[0].bar_label(axes[0].containers[6])
#
##df_house_pct = df_house.pct_change() * 100
##ax_twinx = axes[0].twinx()
##ax_twinx.plot(df_house_pct.index.strftime("%Y"), df_house_pct, color = "r")
##ax_twinx.set_ylabel("年增长率（%）")
#
## area per capita
#df_house = df['居住房屋', '合计']
#df_pop = msd.load("../../人口/人口.csv")
#df_apc = df_house / df_pop.loc[df_house.index,'常住人口']['常住人口']
#axes[1].bar(df_apc.index.strftime("%Y"), df_apc)
#axes[1].set_title("分摊到常住人口（平米/人）")
#axes[1].set_ylabel("面积（平米）")
#axes[1].bar_label(axes[1].containers[0])    