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

module_fn = 'MyStaticsData.py'
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
import MyStaticsData as msd

def excel_to_cvs(excel_fp:str, cvs_fp_prefix:str):
    sheet_df_dicts = pd.read_excel(excel_fp, sheet_name=None)

    for name, df in sheet_df_dicts.items():
        df.columns = [re.sub(r"[  　]",  '', s) for s in df.columns]
        for i in range(len(df)):
            df.iloc[i,0] = re.sub(r"[  　]",  '', df.iloc[i,0])
        df.to_csv(f"{cvs_fp_prefix}_{name}.csv", index=False)


combined_df = msd.load_raw()

#combined_df.to_excel("a.xlsx")
    

    