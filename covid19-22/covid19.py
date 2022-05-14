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

def scrape(df):
    municipalities = ['北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '兵团']
    df_new = pd.DataFrame()
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 0)
    profile.update_preferences()
    with webdriver.Firefox(executable_path='geckodriver', firefox_profile=profile) as driver:
        driver.get("http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml")
    
        ul_list_xpath = "/html/body/div[3]/div[2]/ul"
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, ul_list_xpath)))
        li_list = driver.find_element_by_xpath(ul_list_xpath).find_elements_by_tag_name('li')
        for li in li_list:
            a = li.find_element_by_tag_name('a')
            print(f"===={a.get_attribute('title')}====")
            # if a.get_attribute('title').find('截至4月23日24时新型冠状病毒肺炎疫情最新情况') == -1:
            if a.get_attribute('title').find('新型冠状病毒肺炎疫情最新情况') == -1:
                continue
            a.click()
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[1])
            div_xpath = '//*[@id="xw_box"]'
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, div_xpath)))
            div = driver.find_element_by_xpath(div_xpath)
            s = div.text
            #print(s)
            pat = re.compile(r"(\d{1,2})月(\d{1,2})日0—24时，31个省（自治区、直辖市）和新疆生产建设兵团报告新增确诊病例\d+例.+?本土病例(\d+)例\*?（(.+?)(?<!（残)）.+?(?:含(\d+)例\*?由无症状感染者转为确诊病例\*?（(.+?)(?<!（残)）)?")
            m = pat.search(s)
            print(m.groups()[:2])
            print(m.groups()[2:4])
            print(m.groups()[4:])
            mu_new_cases = {}
            if m:
                month, day = int(m.groups()[0]), int(m.groups()[1])
                mu_new_cases[('新增病例', '全国合计')] = int(m.groups()[2])
                # print(f"全国合计：{int(m.groups()[2])}")
                m2 = re.match('^均?在(.+)$', m.groups()[3])
                if m2:
                    k, = m2.groups()
                    for mu in municipalities:
                        if mu in k:
                            mu_new_cases[('新增病例', mu)] = int(m.groups()[2])
                            # print(f"{mu}: {m.groups()[2]}")
                else:
                    # vv = 0
                    for x in m.groups()[3].split('；'):
                        for y in x.split('，'):
                            # print(y)
                            m2 = re.match('^(.+?)(\d+)例\*?$', y)
                            if m2:
                                k, v = m2.groups()
                                for mu in municipalities:
                                    if mu in k and '吉林市' not in k and '河北区' not in k:
                                        mu_new_cases[('新增病例', mu)] = int(v)
                                        # vv += int(v)
                                        # print(f"{mu}: {v}")
                    # print(f"vv = {vv}")
                if m.groups()[4]: 
                    mu_new_cases[('新增病例', '全国合计')] -= int(m.groups()[4])
                    # print(f"全国合计：{int(m.groups()[4])}")
                if m.groups()[5]:
                    m2 = re.match('^均?在(.+)$', m.groups()[5])
                    if m2:
                        k, = m2.groups()
                        for mu in municipalities:
                            if mu in k:
                                mu_new_cases[('新增病例', mu)] -= int(m.groups()[4])
                                # print(f"{mu}: {m.groups()[4]}")
                    else:
                        # vv = 0
                        for x in m.groups()[5].split('；'):
                            for y in x.split('，'):
                                m2 = re.match('^(.+?)(\d+)例\*?$', y)
                                if m2:
                                    k, v = m2.groups()
                                    for mu in municipalities:
                                        if mu in k and '吉林市' not in k and '河北区' not in k:
                                            mu_new_cases[('新增病例', mu)] -= int(v)
                                            # print(f"{mu}: {v}")
                                            # vv += int(v)
                        # print(f"vv = {vv}")
            pat = re.compile(r"31个省（自治区、直辖市）和新疆生产建设兵团报告新增无症状感染者\d+例.+?本土(\d+)例（(.+?)(?<!（残)）")
            m = pat.search(s)
            if m:
                print(m.groups())
                mu_new_cases[('新增病例', '全国合计')] += int(m.groups()[0])
                # print(f"全国合计：{int(m.groups()[0])}")
                m2 = re.match('^均?在(.+)$', m.groups()[1])
                if m2:
                    k, = m2.groups()
                    for mu in municipalities:
                        if mu in k:
                            mu_new_cases[('新增病例', mu)] = mu_new_cases.setdefault(('新增病例', mu), 0)
                            mu_new_cases[('新增病例', mu)] += int(m.groups()[0])
                else:
                    # vv = 0
                    for x in m.groups()[1].split('；'):
                        for y in x.split('，'):
                            for z in y.split('、'):
                                m2 = re.match('^(?:其中)?(.+?)(\d+)例$', z)
                                if m2:
                                    k, v = m2.groups()
                                    for mu in municipalities:
                                        if mu in k and '吉林市' not in k and '河北区' not in k:
                                            mu_new_cases[('新增病例', mu)] = mu_new_cases.setdefault(('新增病例', mu), 0)
                                            mu_new_cases[('新增病例', mu)] += int(v)
                                            # vv += int(v)
                                            # print(f"{mu}: {v}")
                    # print(f"vv = {vv}")

            pat = re.compile(r"新增死亡病例(\d+)例(.+?)；")
            m = pat.search(s)
            if m:
                print(m.groups())
                mu_new_cases[('新增死亡', '全国合计')] = int(m.groups()[0])
                pat = re.compile(r'^.*?均?为本土病例，均?在(.+?)$')
                m2 = re.match(pat, m.groups()[1])
                if m2:
                    k, = m2.groups()
                    for mu in municipalities:
                        if mu in k:
                            mu_new_cases[('新增死亡', mu)] = int(m.groups()[0])
                else:
                    raise Exception(f"{m2.groups()}")

            dt = pd.Period(year = 2022, month = month, day = day, freq = 'D')
            if not df.empty:
                if dt in df.index:
                    break
            df_day = pd.DataFrame(mu_new_cases, index = [dt])
            print(df_day)
            # print(df_day.columns)
            df_new = df_day if df_new.empty else df_new.combine_first(df_day)
            # print(df_new)

            time.sleep(1)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    return df_new.sort_index()

def scrape_and_save(df):
    df2 = scrape(df)
    if (df2['新增病例'].drop('全国合计', axis = 1).sum(axis = 1) == df2[('新增病例', '全国合计')]).all() and (df2['新增死亡'].drop('全国合计', axis = 1).sum(axis = 1) == df2[('新增死亡', '全国合计')]).all():
        df = df.combine_first(df2)
        df = msd.df_sort_multilevel_values(df, df.index[-1], axis = 1, ascending=False)
        df.to_csv('每日新增病例.csv')
    
    return df

df2 = df['新增病例'].drop(['全国合计'], axis = 1).iloc[-7:,1:10].fillna(0).astype('int64')
fig, axes = plt.subplots(1, 1)
ax = df2.plot.area(ax = axes, title = '近7日全国每日新增病例数前10（不包括上海）')

msd.annotate_area_values(ax, df2)
msd.format_xaxis(ax, '%m-%d')
