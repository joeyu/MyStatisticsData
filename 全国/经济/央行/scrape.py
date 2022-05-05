import io
import json
import logging
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fontTools.ttLib import TTFont
from matplotlib.patches import Patch
from regex import E
from scipy.optimize import curve_fit
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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


def pd_read_html_post_process(df):
    df = df.set_index(0)
    # trim all nan columns
    df = df.loc[:,df.apply(lambda x: not msd.ser_is_identical(x))]
    # fetch unit
    for i in range(len(df)):
        unit_str = df.iloc[i,0]
        m = re.match(r'^单位：(.+)元人民币$', unit_str)
        if m:
            if m.group(1) == '万亿':
                unit = 1E12
            elif m.group(1) == '亿':
                unit = 1E8
            break

    df = df[df.apply(lambda x: not msd.ser_is_identical(x) and msd.is_float(x).all(), axis = 1)]
    df = df.T
    df = df.set_index(df.columns[0])
    df = df[~df.index.duplicated()]
    df.index = pd.DatetimeIndex(df.index).to_period(freq = "M").to_timestamp(freq = "M")
    df = df.astype('float64') * unit
    return df

def webdriver_find_text_link(driver, text, alt_text = None):
    alt_xpath = f".//a[text()='{alt_text}']" if alt_text else ".//a"
    elem = driver.find_element_by_xpath(f"//*[contains(text(),'{text}')]")
    # print("a: (" + elem.text + ")")
    if elem.tag_name == 'a':
        return elem
    else:
        while True:
            elem = elem.find_element_by_xpath('..')
            # print(elem.get_attribute('innerHTML'))
            try:
                alt_elem = elem.find_element_by_xpath(alt_xpath)
            except exceptions.NoSuchElementException:
                continue 
            else:
                if alt_elem:
                    # print(alt_elem.get_attribute('href'))
                    return alt_elem
    

def scrape(link_path, periods):
    Path(link_path).mkdir(parents=True, exist_ok=True)
    if type(periods) is int:
        periods = [periods]
    else:
        periods = range(periods[0], periods[1] - 1, -1)
    
    lp = link_path.split('/')
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 0)
    profile.update_preferences()
    dfs =[]
    with webdriver.Firefox(executable_path='geckodriver', firefox_profile=profile) as driver:
        driver.get("http://www.pbc.gov.cn/diaochatongjisi/116219/116319/index.html")

        table_xpath = "/html/body/div[4]/table[2]/tbody/tr/td[3]/table/tbody/tr/td/div/div[1]/div[2]/table/tbody/tr/td"
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, table_xpath)))
        for a in driver.find_element_by_xpath(table_xpath).find_elements_by_tag_name('a'):
            if any([str(x) in a.text for x in periods]):
                year = [x for x in periods if str(x) in a.text][0]
                print(a.text)
                # a.click()
                driver.execute_script('window.open(arguments[0]);', a.get_attribute('href'))
                WebDriverWait(driver, 20).until(EC.number_of_windows_to_be(2))
                driver.switch_to.window(driver.window_handles[1])
                div_xpath = f"//a[contains(text(),'{lp[0]}')]"
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, div_xpath)))
                a2 = driver.find_element_by_xpath(div_xpath)
                a2.click()
                a3 = webdriver_find_text_link(driver, lp[1], 'htm')
                driver.execute_script("arguments[0].removeAttribute('target')", a3)
                a3.click()
                table_xpath = "//table" 
                table_html = driver.find_element_by_xpath(table_xpath).get_attribute('outerHTML')
                table_html = msd.str_remove_duplicated_whitespaces(table_html)
                df = pd.read_html(table_html)[0]
                df = pd_read_html_post_process(df)
                df.to_csv(f"{link_path}/{year}.csv")
                print(df)
                dfs.append(df)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
    
    # return pd.concat(dfs).sort_index()
    return dfs


    
# df = get_raw_df()
# df = convert(df)

# link_path = '金融机构信贷收支统计/金融机构本外币信贷收支表'
link_path = '社会融资规模/社会融资规模存量统计表'
df = scrape(link_path, 2022)

# profile = webdriver.FirefoxProfile()
# profile.set_preference("network.proxy.type", 0)
# profile.update_preferences()
# with webdriver.Firefox(executable_path='geckodriver', firefox_profile=profile) as driver:
#     driver.get("http://www.pbc.gov.cn/diaochatongjisi/resource/cms/2022/04/2022041516051915430.htm")

#     table_xpath = "//table"
#     # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, table_xpath)))
#     table_html = driver.find_element_by_xpath(table_xpath).get_attribute('outerHTML')
#     df = pd.read_html(table_html)[0]
    
 
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




