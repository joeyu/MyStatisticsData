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
ser_new_cases = df['上海市'].dropna().astype('int64')

# new_cases = {}
# profile = webdriver.FirefoxProfile()
# profile.set_preference("network.proxy.type", 0)
# profile.update_preferences()
# with webdriver.Firefox(executable_path='geckodriver', firefox_profile=profile) as driver:
#     driver.get("https://wsjkw.sh.gov.cn/yqtb/index.html")

#     ul_list_xpath = "/html/body/div[2]/div[3]/div[2]/div/ul"
#     WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, ul_list_xpath)))
#     li_list = driver.find_element_by_xpath(ul_list_xpath).find_elements_by_tag_name('li')
#     end = False
#     for li in li_list:
#         if li.find_element_by_tag_name('a').get_attribute('title').find('新增本土新冠肺炎确诊病例') == -1:
#             continue
#         #dt = li.find_element_by_tag_name('em').text
#         li.click()
#         WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
#         driver.switch_to.window(driver.window_handles[1])
#         div_xpath = '//*[@id="ivs_content"]'
#         WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, div_xpath)))
#         div = driver.find_element_by_xpath(div_xpath)
#         s = div.text
#         #print(s)
#         pat = re.compile(r"2022年(\d{1,2})月(\d{1,2})日.+?新增本土新冠肺炎确诊病例(\d+)例.+?无症状感染者(\d+)例.+?(?:其中(\d+)例确诊病例为此前无症状感染者转归)?")
#         m = pat.search(s)
#         print(m.groups())
#         if m:
#             month, day, new_cases1, new_cases2, new_cases3 = (int(x) if x else 0 for x in m.groups())
#         dt = datetime(2022, month, day)
#         new_cases[dt] = new_cases.setdefault(dt, 0)
#         new_cases[dt] += new_cases1 + new_cases2 - new_cases3

#         if dt in new_cases_merged:
#             break
#         time.sleep(1)
#         driver.close()
#         driver.switch_to.window(driver.window_handles[0])

#new_cases_merged = {**new_cases_merged, **new_cases}

mpl.rc('font', family = 'SimHei', size = 12)
# plt.rcParams.update({
#     "text.usetex": True,
#     "font.family": "sans-serif",
#     "font.sans-serif": ["Helvetica"]})

#ser_new_cases = ser_new_cases[:datetime(2022, 4, 8)]
fig, axes = plt.subplots(1, 1)
def fit_func(x, a, b, c):
    return a * np.exp(b * x) + c
ax = msd.covid19_plot(ser_new_cases, axes, fit_func, 7, traceback = '2022-3-18')

arrowprops=dict(facecolor='cyan', shrink=0.05)
bbox=dict(facecolor='beige')
x = datetime(2022, 3, 28)
y = ser_new_cases[x]
ax.annotate("浦东、浦南及毗邻区域封控", xy =(x, y + 4000), xytext = (x - timedelta(0) , y + 10000), arrowprops = arrowprops, bbox = bbox, ha = 'center')
x = datetime(2022, 4, 1)
y = ser_new_cases[x]
ax.annotate("浦西封控", xy =(x, y + 4000), xytext = (x - timedelta(0), y + 10000), arrowprops = arrowprops, bbox = bbox, ha = 'center')
