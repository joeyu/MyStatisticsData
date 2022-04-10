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

new_cases_merged = {
    '2022-03-03': 16,
    '2022-03-04': 19,
    '2022-03-05': 28,
    '2022-03-06': 48,
    '2022-03-07': 55,
    '2022-03-08': 65,
    '2022-03-09': 80,
    '2022-03-10': 75,
    '2022-03-11': 83,
    '2022-03-12': 65,
    '2022-03-13': 167,
    '2022-03-14': 139,
    '2022-03-15': 202,
    '2022-03-16': 158,
    '2022-03-17': 260,
    '2022-03-18': 374,
    '2022-03-19': 503,
    '2022-03-20': 758,
    '2022-03-21': 896,
    '2022-03-22': 981,
    '2022-03-23': 983,
    '2022-03-24': 1609,
    '2022-03-25': 2264,
    '2022-03-26': 2676,
    '2022-03-27': 3500,
    '2022-03-28': 4456,
    '2022-03-29': 5964,
    '2022-03-30': 5637,
    '2022-03-31': 4482,
    '2022-04-01': 6309,
    '2022-04-02': 8153,
    '2022-04-03': 8935,
    '2022-04-04': 13350,
    '2022-04-05': 17037,
    '2022-04-06': 19967,
    '2022-04-07': 20899,
    '2022-04-08': 23204,
    '2022-04-09': 24752,
}

new_cases_merged = {datetime.strptime(dt, '%Y-%m-%d'): v for dt, v in new_cases_merged.items()}

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

ser_new_cases = pd.Series(new_cases_merged)
#ser_new_cases = ser_new_cases[:datetime(2022, 4, 8)]
ax = ser_new_cases.plot(title = '上海市新冠每日新增病例及趋势', marker = 'd', color = 'r', label = "历史每日新增病例数")
ax.set_xlabel("t", fontsize = 15)    
ax.set_ylabel("病例数I", fontsize = 15)    
n_day = np.arange(len(ser_new_cases))
def fun(x, a, b, c):
    return a * np.exp(b * x) + c
popt, pcov = curve_fit(fun, n_day, ser_new_cases)
a, b, c = popt
days = len(ser_new_cases) + 7
ser_new_cases_fit = pd.Series(np.arange(days)).apply(lambda x: int(a * np.exp(b * x) + c))
ser_new_cases_fit.index = pd.date_range(ser_new_cases.index[0], periods = days, freq='D')
ax = ser_new_cases_fit.plot(ax = ax, linestyle = '--', marker ='o', color = 'b', label = "拟合数及趋势")
# x_ticklabels = [x.strftime('%m-%d') for x in ser_new_cases_fit.index]
y0, y1 = ax.get_ylim()
offset = y1 / 100 
for k, v in ser_new_cases.iteritems():
    offset2 = offset if v > ser_new_cases_fit.get(k, 0) else -offset * 2
    ax.text(k, v + offset2, v, color = 'r', ha='center') 
for k, v in ser_new_cases_fit.iteritems():
    offset2 = offset if v > ser_new_cases.get(k, 0) else -offset * 2
    ax.text(k, v + offset2, v, color = 'b', ha='center')  


legend = ax.legend(loc='upper left')

ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m-%d'))
ax.grid(which='both', axis = 'x')
#ax.grid(which='minor', axis = 'x')
# ax.set_xticklabels(ax.get_xticks(), rotation = 45)
for label in ax.get_xticklabels(which = 'both'): 
    label.set_rotation(45)

x = ser_new_cases_fit.index[int(len(ser_new_cases_fit) * 0.7)]
y0, y1 = ax.get_ylim()
y = int((y1 - y0) * 0.8)
s = f'$I_T(t) = {a:.2f}e^{{{b:.3f}t}}{c:+.1f}$'
# ax.text(x, y, s, color = 'b', fontsize = 18, bbox=dict(facecolor='ivory'))
#arrowprops=dict(facecolor='ivory', shrink=0.05)
arrowprops=None
bbox=dict(facecolor='beige')
ax.annotate(s, xy = (0.98, 0.9), xycoords = 'axes fraction', xytext = (0.75, 0.9), textcoords = 'axes fraction', arrowprops = arrowprops, bbox = bbox, color = 'blue', size = 18)

arrowprops=dict(facecolor='cyan', shrink=0.05)
bbox=dict(facecolor='beige')
x = datetime(2022, 3, 28)
y = ser_new_cases[x]
ax.annotate("浦东、浦南及毗邻区域封控", xy =(x, y + 4000), xytext = (x - timedelta(0) , y + 10000), arrowprops = arrowprops, bbox = bbox, ha = 'center')
x = datetime(2022, 4, 1)
y = ser_new_cases[x]
ax.annotate("浦西封控", xy =(x, y + 4000), xytext = (x - timedelta(0), y + 10000), arrowprops = arrowprops, bbox = bbox, ha = 'center')

def fits(new_cases, start):
    bt_array = [] 
    while start in new_cases:
        bt_new_cases = new_cases[:start]
        n_day = np.arange(len(bt_new_cases))
        popt, pcov = curve_fit(fun, n_day, bt_new_cases)
        bt_array.append(popt)
        start += timedelta(1)
    
    a = np.array([p[0] for p in bt_array])
    b = np.array([p[1] for p in bt_array])
    exp = np.exp(b)
    return exp

start = datetime(2022, 3, 18)
rate = fits(ser_new_cases, start)
rate_index = ser_new_cases[start:].index
ax_twinx = ax.twinx()
line, = ax_twinx.plot(rate_index, rate, color = 'purple', linestyle = '--', marker = 'x')
ax_twinx.set_ylabel("日增长率", fontsize = 15, color = 'purple')
# y0, y1 = ax_twinx.get_ylim()
rate_max = rate.max()
rate_min = rate.min()
rate_residual = rate_max - rate_min
y0 = rate_min - rate_residual * 2
y1 = rate_max + rate_residual * 1
ax_twinx.set_ylim(y0, y1)
for k, v in zip(rate_index, rate):
    ax_twinx.text(k, v + 0.01, round(v, 3), color = 'purple', ha = 'center')

# s = r'$\frac{I^T_{(t+1)}}{I^T_{(t)}}$'
s = r'$e^{b(t)}$'
#arrowprops=dict(facecolor='ivory', shrink=0.05)
arrowprops=None
bbox=dict(facecolor='beige')
ax_twinx.annotate(s, xy = (rate_index[0], rate[0]), xycoords = 'data', xytext = (rate_index[0] - timedelta(2), rate[0] + 0.1), textcoords = 'data', arrowprops = arrowprops, color = 'purple', bbox = bbox, size = 20)

ax = legend.axes
handles, labels = ax.get_legend_handles_labels()
handles.append(line)
labels.append("拟合数日增长率")
legend._legend_box = None
legend._init_legend_box(handles, labels)
legend._set_loc(legend._loc)