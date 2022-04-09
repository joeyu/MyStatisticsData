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


mpl.rc('font', family = 'SimHei', size = 12)

new_cases_merged = {
    '2022-03-01': 64,
     '2022-03-02': 10,
     '2022-03-03': 16,
     '2022-03-04': 43,
     '2022-03-05': 61,
     '2022-03-06': 66,
     '2022-03-07': 75,
     '2022-03-08': 174,
     '2022-03-09': 344,
     '2022-03-10': 246,
     '2022-03-11': 400,
     '2022-03-12': 2156,
     '2022-03-13': 1026,
     '2022-03-14': 4067,
     '2022-03-15': 1853,
     '2022-03-16': 1157,
     '2022-03-17': 2353,
     '2022-03-18': 2211,
     '2022-03-19': 1494,
     '2022-03-20': 2091,
     '2022-03-21': 2465,
     '2022-03-22': 2848,
     '2022-03-23': 2601,
     '2022-03-24': 2010,
     '2022-03-25': 2496,
     '2022-03-26': 2078,
     '2022-03-27': 1993,
     '2022-03-28': 1867,
     '2022-03-29': 2182,
     '2022-03-30': 2175,
     '2022-03-31': 2234,
     '2022-04-01': 2974,
     '2022-04-02': 4455,
     '2022-04-03': 3578,
     '2022-04-04': 2472,
     '2022-04-05': 2771,
     '2022-04-06': 2436,
     '2022-04-07': 2266,
     '2022-04-08': 954
}

new_cases_merged = {datetime.strptime(dt, '%Y-%m-%d'): v for dt, v in new_cases_merged.items()}
new_cases = {}

profile = webdriver.FirefoxProfile()
profile.set_preference("network.proxy.type", 0)
profile.update_preferences()
with webdriver.Firefox(executable_path='geckodriver', firefox_profile=profile) as driver:
    driver.get("http://www.jl.gov.cn/szfzt/jlzxd/yqtb/index.html")

    ul_list_xpath = "/html/body/div[2]/ul"
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, ul_list_xpath)))
    li_list = driver.find_element_by_xpath(ul_list_xpath).find_elements_by_tag_name('li')
    end = False
    for li in li_list:
        if li.find_element_by_tag_name('a').get_attribute('title').find('吉林省卫生健康委关于新型冠状病毒肺炎疫情情况通报') == -1:
            continue
        #dt = li.find_element_by_tag_name('em').text
        li.click()
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[1])
        div_xpath = "/html/body/div[1]/div[3]/div[2]/div"
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, div_xpath)))
        div = driver.find_element_by_xpath(div_xpath)
        s = div.text
        print(s)
        pat = re.compile(r"(\d{1,2})月(\d{1,2})日.+?全省新增本地确诊病例(?:（轻型）)?(\d+)例.+?(?:新增本地)?无症状感染者(\d+)例")
        match = pat.findall(s)
        for m in match:
            print(m)
            if len(m) == 4:
                month, day, new_case1, new_case2 = (int(x) for x in m)
            elif len(m) == 2:
                month, day = (int(x) for x in m)
                new_case1, new_case2 = 0, 0

            dt = datetime(2022, month, day)
            new_cases[dt] = new_cases.setdefault(dt, 0)
            new_cases[dt] += new_case1 + new_case2

        if dt in new_cases_merged:
            break
        time.sleep(1)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])



new_cases_merged = {**new_cases_merged, **new_cases}

ser_new_cases = pd.Series(new_cases_merged)
ax = ser_new_cases.plot(title = "吉林省新冠每日新增病例", marker = 'x', color = 'r', label = "历史病例数")
for k, v in ser_new_cases.iteritems():
    offset = 100
    ax.text(k, v + offset, v, color = 'r')  

ax.legend()

ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m-%d'))
ax.grid(which='both', axis = 'x')
# ax.grid(which='minor', axis = 'x')
for label in ax.get_xticklabels(which = 'both'): 
    label.set_rotation(45)
