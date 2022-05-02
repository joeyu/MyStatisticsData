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

def cleanup(df):
    df = df.set_index(0)
    df = df.loc[:,df.apply(lambda x: not msd.ser_is_identical(x))]
    df = df[df.apply(lambda x: not msd.ser_is_identical(x) and msd.is_float(x).all(), axis = 1)]
    df = df.T.set_index(df.index[0]).astype('float64') * 1E8
    df.index = pd.DatetimeIndex(df.index).to_period().to_timestamp(freq = "M")
    return df

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
                div_xpath = '/html/body/div[4]/table[2]/tbody/tr/td[3]'
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, div_xpath)))
                div = driver.find_element_by_xpath(div_xpath)
                for a2 in div.find_elements_by_tag_name('a'):
                    if lp[0] in a2.text:
                        print(a2.text)
                        a2.click()
                        div_xpath = '/html/body/div[4]/div/table/tbody/tr/td/table/tbody/tr/td/div/table[3]/tbody/tr/td'
                        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, div_xpath)))
                        div = driver.find_element_by_xpath(div_xpath)
                        for t in div.find_elements_by_tag_name('table'):
                            html = t.find_element_by_xpath('./tbody/tr/td').get_attribute('innerHTML')
                            if lp[1] in html:
                                print(html)
                                a3 = t.find_element_by_xpath(f"//a[contains(text(), '{lp[1]}') or text() = 'htm']")
                                driver.execute_script("arguments[0].removeAttribute('target')", a3)
                                a3.click()
                                table_xpath = "//table" 
                                # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, table_xpath)))
                                table_html = driver.find_element_by_xpath(table_xpath).get_attribute('outerHTML')
                                table_html = msd.remove_duplicated_whitespaces(table_html)
                                df = pd.read_html(table_html)[0]
                                df = cleanup(df)
                                df.to_csv(f"{link_path}/{year}.csv")
                                print(df)
                                dfs.append(df)
                                break
                        break

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
    
    # return pd.concat(dfs).sort_index()
    return dfs

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

    
# df = get_raw_df()
# df = convert(df)


df = scrape('金融机构信贷收支统计/金融机构本外币信贷收支表', (2022, 2006))

 
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




