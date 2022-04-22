# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 20:59:42 2022

@author: Zhou Yu
"""
from pathlib import Path
import subprocess
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from fontTools.ttLib import TTFont
import numpy as np
from pathlib import Path
import io
import json
import matplotlib.dates as mdates
from datetime import datetime, timedelta
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


# mpl.rc('font', family = 'SimHei', size = 12)
df = msd.load()
ser_new_cases = df['吉林省'].dropna().astype('int64')

def scrape(ser_new_cases):
    new_new_cases = {}
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 0)
    profile.update_preferences()
    with webdriver.Firefox(executable_path='geckodriver', firefox_profile=profile) as driver:
        driver.get("http://www.jl.gov.cn/szfzt/jlzxd/yqtb/index.html")

        ul_list_xpath = "/html/body/div[2]/ul"
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, ul_list_xpath)))
        li_list = driver.find_element_by_xpath(ul_list_xpath).find_elements_by_tag_name('li')
        for li in li_list:
            if li.find_element_by_tag_name('a').get_attribute('title').find('吉林省卫生健康委关于新型冠状病毒肺炎疫情情况通报') == -1:
                continue
            #dt = li.find_element_by_tag_name('em').text
            li.click()
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[1])
            div_xpath = "/html/body/div[1]/div[3]/div[2]/div/div"
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, div_xpath)))
            div = driver.find_element_by_xpath(div_xpath)
            s = div.text
            print(s)
            pat = re.compile(r"(\d{1,2})月(\d{1,2})日.+?全省新增本地确诊病例(?:（轻型）)?(\d+)例.+?(?:新增本地)?无症状感染者(\d+)例")
            m= pat.search(s)
            print(m.groups())
            if m:
                month, day, new_cases1, new_cases2 = (int(x) for x in m.groups())
            pat = re.compile(r"含(\d+)例无症状感染者转为确诊病例")
            m = pat.findall(s)
            print(m)
            new_cases3 = np.array(m).astype(int).sum() if m else 0
            dt = pd.Period(year = 2022, month = month, day = day, freq = 'D')
            if dt in ser_new_cases:
                break
            new_new_cases[dt] = new_new_cases.setdefault(dt, 0)
            new_new_cases[dt] += new_cases1 + new_cases2 -new_cases3

            time.sleep(1)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    
    return pd.concat([ser_new_cases, pd.Series(new_new_cases)]).sort_index()

# df = df.drop('吉林省', axis = 1).merge(ser_new_cases.to_frame(name = '吉林省'), how = 'outer', left_index=True, right_index=True)
df = df.combine_first(ser_new_cases.to_frame(name = '吉林省'))

fig, axes = plt.subplots(1, 1)
ax = msd.covid19_plot(ser_new_cases, axes)

# fig, axes = plt.subplots(1, 1)
# ax = ser_new_cases.plot(ax = axes, title = "吉林省新冠每日新增病例", marker = 'x', color = 'r', label = "历史病例数")
# for k, v in ser_new_cases.iteritems():
#     offset = 100
#     ax.text(k, v + offset, v, color = 'r')  

# ax.legend()

# ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
# ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m-%d'))
# ax.grid(which='both', axis = 'x')
# # ax.grid(which='minor', axis = 'x')
# for label in ax.get_xticklabels(which = 'both'): 
#     label.set_rotation(45)
