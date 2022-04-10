# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 09:29:53 2022

@author: Zhou Yu
"""
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
from selenium.common.exceptions import NoSuchElementException

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

df = msd.load()
ser_new_cases = df['广州市'].dropna().astype('int64')
new_new_cases = {}

new_cases = {}
profile = webdriver.FirefoxProfile()
profile.set_preference("network.proxy.type", 0)
profile.update_preferences()
with webdriver.Firefox(executable_path='geckodriver', firefox_profile=profile) as driver:
    driver.get("http://wjw.gz.gov.cn/ztzl/xxfyyqfk/yqtb/")

    ul_list_xpath = "/html/body/div/div[3]/div[3]/div[2]/ul"
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, ul_list_xpath)))
    li_list = driver.find_element_by_xpath(ul_list_xpath).find_elements_by_tag_name('li')
    end = False
    for li in li_list:
        try:
            a = li.find_element_by_tag_name('a')
        except NoSuchElementException:
            continue
        if a.get_attribute('title').find('广州市新冠肺炎疫情情况') == -1:
            continue
        #dt = li.find_element_by_tag_name('em').text
        print(li.text)
        a.click()
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[1])
        div_xpath = '/html/body/div/div[3]/div[3]/div[2]/div[2]'
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, div_xpath)))
        div = driver.find_element_by_xpath(div_xpath)
        s = div.text
        #print(s)
        pat = re.compile(r"2022年(\d{1,2})月(\d{1,2})日.+?全市新增本土确诊病例(\d+)例(?:（其中(\d+)例为此前报告的无症状感染者转确诊）)?.+?本土无症状感染者(\d+)例")
        m = pat.search(s)
        print(m.groups())
        if m:
            month, day, new_cases1, new_cases2, new_cases3 = (int(x) if x else 0 for x in m.groups())
        dt = pd.Period(year = 2022, month = month, day = day, freq = 'D')
        new_cases = {}
        new_cases[dt] = new_cases.setdefault(dt, 0)
        new_cases[dt] += new_cases1 - new_cases2 + new_cases3

        if dt in ser_new_cases:
            break
        new_new_cases = {**new_new_cases, **new_cases}
        time.sleep(1)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

#new_cases_merged = {**new_cases_merged, **new_cases}

mpl.rc('font', family = 'SimHei', size = 12)
# plt.rcParams.update({
#     "text.usetex": True,
#     "font.family": "sans-serif",
#     "font.sans-serif": ["Helvetica"]})

ser_new_new_cases = pd.Series(new_new_cases)
ser_new_cases = pd.concat([ser_new_cases, ser_new_new_cases]).sort_index()
df = df.drop('广州市', axis = 1).merge(ser_new_cases.to_frame(name = '广州市'), how = 'outer', left_index=True, right_index=True)

ax = ser_new_cases.plot(title = "广州市新冠每日新增病例", marker = 'x', color = 'r', label = "历史病例数")
for k, v in ser_new_cases.iteritems():
    offset = 0.1
    ax.text(k, v + offset, v, color = 'r')  

ax.legend()

ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m-%d'))
ax.grid(which='both', axis = 'x')
# ax.grid(which='minor', axis = 'x')
for label in ax.get_xticklabels(which = 'both'): 
    label.set_rotation(45)