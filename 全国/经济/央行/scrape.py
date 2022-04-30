import logging
import sys
import re
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
from fontTools.ttLib import TTFont
import numpy as np
from pathlib import Path
import io
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scipy.optimize import curve_fit
import time
import sys

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

def get_raw_df():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 0)
    profile.update_preferences()
    with webdriver.Firefox(executable_path='geckodriver', firefox_profile=profile) as driver:
        driver.get("http://www.pbc.gov.cn/diaochatongjisi/resource/cms/2022/04/2022041516061719456.htm")

        table_xpath = "/html/body/div/table" 
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, table_xpath)))
        table_html = driver.find_element_by_xpath(table_xpath).get_attribute('outerHTML')
        df = pd.read_html(table_html)[0]
    
    return df

df = get_raw_df()

df = df.set_index(0)
df = df.loc[:,df.apply(lambda x: x.unique().size != 1)]
df = df[df.apply(lambda x: x.unique().size != 1, axis = 1)]
df = df.T.set_index(df.index[0]).astype('float64') * 1E8
df.index = pd.DatetimeIndex(df.index).to_period().to_timestamp(freq = "M")



 
#    if 
#rows = []
#
#for i in range(len(df)):
#    if df.iloc[i] if row.unique().size > 2:
#        continue
#    
#    try:
#        cols = pd.DatetimeIndex(row)
#        cols.to_period().to_timestamp(freq = 'M')
#        t_i = i + 1
#    except pd.errors.ParserError:
#        t_len += 1
#        continue
#
#if len(df.columns) > 12:
#    df = df.iloc[:,:12]
#df = df.iloc[i+1:]




