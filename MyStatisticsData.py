import logging
import re
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
from fontTools.ttLib import TTFont
import numpy as np
from pathlib import Path
import io
import json
from datetime import datetime, timedelta
from scipy.optimize import curve_fit

logging.basicConfig(level=logging.INFO)

def load_meta(meta_fp:str):
    with io.open(meta_fp, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return meta

def load(data_fp:str = '.'):
    """
    Loads raw data from all stored .csv files
    """
    meta_fn = 'meta.json'

    if type(data_fp) == str:
        data_fp = [data_fp]

    df_array = []
    for fp in data_fp:
        fp = Path(fp).resolve()
        if fp.is_dir():
            fp_array = (fp.glob('*.csv'))
            meta_fn = str(fp / meta_fn)
        else:
            fp_array = [fp]
            meta_fn = str(fp.parent / meta_fn)

        meta = load_meta(meta_fn)

        df_freq_groups = {}
        for fp in fp_array:
            logging.info(f"Reading '{fp}'...")
            if 'header' in meta:
                header = meta['header']
            else:
                with open(fp, encoding='utf8') as f:
                    lines = f.readlines()
                    for i, l in enumerate(lines):
                        first_item = l.split(',')[0]
                        try:
                            pd.Period(first_item)
                        except:
                            continue
                        else:
                            break
                    header = list(range(i))
            index_col = 0
            df = pd.read_csv(fp, index_col = index_col, header = header, comment = "#")
            df.index = pd.PeriodIndex([pd.Period(i) for i in df.index])

            freqstr = df.index.freqstr
            df_freq_groups.setdefault(freqstr, pd.DataFrame())
            df_freq_groups[freqstr] = pd.concat([df_freq_groups[freqstr], df])

        df_array.extend([df.sort_index(axis = 0) for df in df_freq_groups.values()])
        
    if len(df_array) == 0:
        df_array = None
    elif len(df_array) == 1:
        df_array = df_array[0]
    return df_array

#Get available system fonts
#import matplotlib.font_manager
#flist = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
#names = [matplotlib.font_manager.FontProperties(fname=fname).get_name() for fname in flist]
#Set font to support Chinese
mpl.rc('font', family = 'SimHei', size = 12)
#mpl.rc('font', family = 'Microsoft New Tai Lue')

def read_raw(raw_filepath, unit = 1E8):
    fp = Path(raw_filepath)
    if fp.is_dir():
        fp_array = (fp.glob('*.csv'))
    else:
        fp_array = [fp]

    for fp in fp_array:
        with open(fp, encoding='utf8') as f:
            items = f.readline().split(',')
            for i, v in enumerate(items):
                try:
                    pd.Period(v)
                except:
                    continue
                else:
                    break
        index_col = list(range(i))
        d = pd.read_csv(fp, index_col = index_col, header=[0])
        d = d.T * unit
        d.to_csv(fp.name)

def plot_bar(df, **kwargs):
    if isinstance(df, pd.core.series.Series):
        df = pd.DataFrame(df)
    
    ax = df.plot.bar(**kwargs)
    for container in ax.containers:
        ax.bar_label(container)

    return ax

def plot(df, **kwargs):
    if isinstance(df, pd.core.series.Series):
        df = pd.DataFrame(df)
    ax = kwargs.pop('ax')
    ylabel = kwargs.pop('ylabel', None)
    ax.set_ylabel(ylabel)
    for col in df:
        ser = df[col]
        ax.plot(ser.index.strftime('%Y'), ser, label = col, **kwargs)
        for k, v in ser.iteritems():
            k = k.strftime('%Y')
            ax.text(k, v + 0.2, v)
    
    axes = ax.get_shared_x_axes().get_siblings(ax)
    if axes[-1] == ax:
        ax.legend()
    
    return ax

def covid19_plot(ser_new_cases, ax, fit_func, fit_func_type, trend_days = 7, traceback = None, annotations = None):
    ax = ser_new_cases.plot(ax = ax, title = ser_new_cases.name + '新冠每日新增病例及趋势', marker = 'd', color = 'r', label = "历史每日新增病例数")
    ax.set_xlabel("t", fontsize = 15)    
    ax.set_ylabel("每日新增病例数", fontsize = 15)    
    n_day = np.arange(len(ser_new_cases))
    popt, pcov = curve_fit(fit_func, n_day, ser_new_cases)
    print(f'pcov: {pcov}')
    if fit_func_type == 'exponential' or fit_func_type == 'quadratic':
        a, b, c = popt
        apply_fit_func = lambda x: int(fit_func(x, a, b, c))
    elif fit_func_type == 'linear':
        a, b = popt
        apply_fit_func = lambda x: int(fit_func(x, a, b))
    days = len(ser_new_cases) + trend_days
    ser_new_cases_fit = pd.Series(np.arange(days)).apply(apply_fit_func)
    ser_new_cases_fit.index = pd.period_range(ser_new_cases.index[0], periods = days, freq='D')
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

    ax.legend(loc='upper left')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m-%d'))
    ax.grid(which='both', axis = 'x')
    for label in ax.get_xticklabels(which = 'both'): 
        label.set_rotation(45)

    x = ser_new_cases_fit.index[int(len(ser_new_cases_fit) * 0.7)]
    y0, y1 = ax.get_ylim()
    y = int((y1 - y0) * 0.8)
    if fit_func_type == 'exponential':
        s = r'$\frac{\mathrm{d}I_T}{\mathrm{d}t} = %.2fe^{%.3ft}%+.1f$' % (a, b, c)
    elif fit_func_type == 'linear':
        s = r'$\frac{\mathrm{d}I_T}{\mathrm{d}t} = %.1ft%+.1f$' % (a, b)
    # ax.text(x, y, s, color = 'b', fontsize = 18, bbox=dict(facecolor='ivory'))
    #arrowprops=dict(facecolor='ivory', shrink=0.05)
    arrowprops=None
    bbox=dict(facecolor='beige')
    ax.annotate(s, xy = (0.98, 0.9), xycoords = 'axes fraction', xytext = (0.70, 0.9), textcoords = 'axes fraction', arrowprops = arrowprops, bbox = bbox, color = 'blue', size = 18)

    def fits(new_cases, start):
        bt_array = [] 
        while start in new_cases:
            bt_new_cases = new_cases[:start]
            n_day = np.arange(len(bt_new_cases))
            popt, pcov = curve_fit(fit_func, n_day, bt_new_cases)
            bt_array.append(popt)
            start += 1
        
        a = np.array([p[0] for p in bt_array])
        b = np.array([p[1] for p in bt_array])
        exp = np.exp(b)
        return exp

    if traceback:
        start = pd.Period(traceback)
        rate = fits(ser_new_cases, start)
        rate_index = ser_new_cases[start:].index
        ax_twinx = ax.twinx()
        line, = ax_twinx.plot(rate_index.to_timestamp(), rate, color = 'purple', linestyle = '--', marker = 'x')
        ax_twinx.set_ylabel("日增长倍数", fontsize = 15, color = 'purple')
        # y0, y1 = ax_twinx.get_ylim()
        rate_max = rate.max()
        rate_min = rate.min()
        rate_residual = rate_max - rate_min
        y0 = rate_min - rate_residual * 3
        y1 = rate_max + rate_residual * 1
        ax_twinx.set_ylim(y0, y1)
        for k, v in zip(rate_index, rate):
            ax_twinx.text(k, v + 0.01, round(v, 3), color = 'purple', ha = 'center')

        # s = r'$\frac{I^T_{(t+1)}}{I^T_{(t)}}$'
        s = r'$e^{b(t)}$'
        #arrowprops=dict(facecolor='ivory', shrink=0.05)
        arrowprops=None
        bbox=dict(facecolor='beige')
        ax_twinx.annotate(s, xy = (rate_index[0], rate[0]), xycoords = 'data', xytext = (-80, 50), textcoords = 'offset points', arrowprops = arrowprops, color = 'purple', bbox = bbox, size = 20)

        legend = ax.get_legend()
        handles, labels = ax.get_legend_handles_labels()
        handles.append(line)
        labels.append("拟合数日增长倍数")
        legend._legend_box = None
        legend._init_legend_box(handles, labels)
        legend._set_loc(legend._loc)

    if annotations:
        arrowprops=dict(facecolor='cyan', shrink=0.05)
        bbox=dict(facecolor='beige')
        for an in annotations:
            x = an['x']
            text = an['text']
            v0, v1 = ser_new_cases[x], ser_new_cases_fit[x]
            y = v0 if v0 > v1 else v1
            y0, y1 = ax.get_ylim()
            dy = (y1 - y0) * 0.04
            ax.annotate(text, xy =(x, y + dy), xytext = (0, 50), textcoords = 'offset points', arrowprops = arrowprops, bbox = bbox, ha = 'center')

    return ax
