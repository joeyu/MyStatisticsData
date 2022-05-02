import logging
import re
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
import matplotlib.patheffects as PathEffects
from fontTools.ttLib import TTFont
import numpy as np
from pathlib import Path
import io
import json
from datetime import datetime, timedelta
from scipy.optimize import curve_fit

logging.basicConfig(level=logging.INFO)

def str_remove_duplicated_whitespaces(s):
    return re.sub(r'\s{2,}', ' ', s)

def df_rename_duplicated_columns(df):
    cols=pd.Series(df.columns)

    for dup in cols[cols.duplicated()].unique(): 
        cols[cols == dup] = [dup + '.' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]

    df.columns = cols

    return df

def df_rename_columns(df, cols:dict):
    ren = {v2: k for k, v in cols.items() for v2 in v}
    return df.rename(columns = ren)

def ser_is_identical(ser, value = None):
    u = ser.unique()
    if u.size != 1:
        return False
    
    if value:
        if u[0] != value:
            return False
    
    return True

def is_float(s):
    if type(s) == pd.Series:
        return s.apply(lambda x: is_float(x))

    try:
        float(s)
    except ValueError:
        return False
    else:
        return True

def multilevel_df_sort_values(df, *args, **kwargs):
    axis = kwargs.get('axis', 0)
    df_sorted = pd.DataFrame()
    if axis == 0:
        levels = df.index.levels
    else:
        levels = df.columns.levels
        for l in levels[-2]:
            df_sorted = pd.concat([df_sorted, df[[l]].sort_values(*args, **kwargs)], axis = 1)
    
    return df_sorted

def multilevel_df_split(df, axis = 0):
    dfs = {}
    if axis == 0:
        keys = pd.MultiIndex.from_product(df.index.levels[:-1])
        for k in keys:
            if k in df:
                dfs[k] = df.loc[k]
    else:
        keys = pd.MultiIndex.from_product(df.columns.levels[:-1])
        for k in keys:
            if k in df:
                dfs[k] = df[k]
    
    return dfs

def load_meta(meta_fp:str):
    with io.open(meta_fp, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return meta

def load(data_fp:str = '.', merge = True):
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

            if merge:
                freqstr = df.index.freqstr
                df_freq_groups.setdefault(freqstr, pd.DataFrame())
                df_freq_groups[freqstr] = pd.concat([df_freq_groups[freqstr], df])
            else:
                df_array.append(df)

        if merge:
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
        if type(ser.name) == tuple:
            ser.name = '/'.join(ser.name)
        freq = ser.index.freqstr
        if freq == 'Y':
            format = '%Y'
        elif freq == 'D':
            format = '%m-%d' 
        ax.plot(ser.index.strftime(format), ser, label = col, **kwargs)
        for k, v in ser.iteritems():
            k = k.strftime(format)
            ax.text(k, v + 0.2, v)
    
    axes = ax.get_shared_x_axes().get_siblings(ax)
    if axes[-1] == ax:
        ax.legend()
    
    return ax

def standard_math_coordinate(ax):
    if ax == None:
        ax = plt.gca()
    ax.spines[['left', 'bottom']].set_position('zero')
    ax.spines[['top', 'right']].set_visible(False)    
    ax.set_aspect('equal')

    return ax

def annotate_plot_line_twins(ax, ser0, ser1):
    if ax == None:
        ax = plt.gca()

    path_effects = [PathEffects.withStroke(linewidth=2, foreground='w')]
    y0, y1 = ax.get_ylim()
    offset = (y1 - y0) / 100 
    for k, v in ser0.iteritems():
        offset2 = offset if v > ser1.get(k, 0) else -offset * 2
        txt = ax.text(k, v + offset2, v, color = 'r', ha='center') 
        txt.set_path_effects(path_effects)
    for k, v in ser1.iteritems():
        offset2 = offset if v > ser0.get(k, 0) else -offset * 2
        txt = ax.text(k, v + offset2, v, color = 'b', ha='center')  
        txt.set_path_effects(path_effects)
    
    return ax

def annotate_plot_line(ax, ser):
    if ax == None:
        ax = plt.gca()

    path_effects = [PathEffects.withStroke(linewidth=2, foreground='w')]
    y0, y1 = ax.get_ylim()
    offset = (y1 - y0) / 100 
    for k, v in ser.iteritems():
        txt = ax.text(k, v + offset, v, color = 'r', ha='center') 
        txt.set_path_effects(path_effects)
    
    return ax

def annotate_area_values(ax, df):
    df2 = df.cumsum(axis = 1) - df / 2
    for i in range(len(df)):
        for y, v in zip(df2.iloc[i], df.iloc[i]):
            txt = ax.text(df2.index[i], y, v, ha = 'center') 
            txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='w')])

def format_xaxis(ax, format):
    if ax == None:
        ax = plt.gca()

    ax.xaxis.set_major_formatter(mdates.DateFormatter(format))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter(format))
    for label in ax.get_xticklabels(which = 'both'): 
        label.set_rotation(45)

def add_legend_entry(ax, line, label):
    if ax == None:
        ax = plt.gca()

    legend = ax.get_legend()
    handles, labels = ax.get_legend_handles_labels()
    handles.append(line)
    labels.append(label)
    legend._legend_box = None
    legend._init_legend_box(handles, labels)
    legend._set_loc(legend._loc)

def linear_fit_func(x, a, b):
    return a * x + b 
def exponential_fit_func(x, a, b, c):
    return a * np.exp(b * x) + c
    
def covid19_plot(ser, ax, fit_func = None, traceback = None, annotations = None):
    ax = ser.plot(ax = ax, title = ser.name[0] + '新冠每日' + ser.name[1] + '及趋势', marker = 'd', color = 'r', label = "历史每日" + ser.name[1] + "数")
    ax.set_xlabel("t", fontsize = 15)    
    ax.set_ylabel("每日" + ser.name[1] + "数", fontsize = 15)    

    if fit_func:
        ser_to_fit = ser[fit_func['start']:] if fit_func['start'] else ser
        n_day = np.arange(len(ser_to_fit))
        popt, pcov = curve_fit(fit_func['func'], n_day, ser_to_fit)
        print(f'pcov: {pcov}')
        if fit_func['type'] == 'exponential' or fit_func['type'] == 'quadratic':
            a, b, c = popt
            apply_fit_func = lambda x: int(fit_func['func'](x, a, b, c))
        elif fit_func['type'] == 'linear':
            a, b = popt
            apply_fit_func = lambda x: int(fit_func['func'](x, a, b))
        days = len(ser_to_fit) + fit_func['trend']
        ser_fit = pd.Series(np.arange(days)).apply(apply_fit_func)
        ser_fit.index = pd.period_range(ser_to_fit.index[0], periods = days, freq='D')
        ax = ser_fit.plot(ax = ax, linestyle = '--', marker ='o', color = 'b', label = "拟合数及趋势")
        annotate_plot_line_twins(ax, ser, ser_fit)

        y0, y1 = ax.get_ylim()
        y = int((y1 - y0) * 0.8)
        if fit_func['type'] == 'exponential':
            s = r'$\frac{\mathrm{d}I_T}{\mathrm{d}t} = %.2fe^{%.3ft}%+.1f$' % (a, b, c)
        elif fit_func['type'] == 'linear':
            s = r'$\frac{\mathrm{d}I_T}{\mathrm{d}t} = %.1ft%+.1f$' % (a, b)
        # arrowprops=dict(facecolor='ivory', shrink=0.05)
        arrowprops = None
        bbox = {'facecolor': 'beige'}
        y = ser_fit[-2]
        _, y = ax.transData.transform((0, y))
        _, y = ax.transAxes.inverted().transform((0, y))
        ax.annotate(s, xy = (0.98, y), xycoords = 'axes fraction', xytext = (0.75, y), textcoords = 'axes fraction', arrowprops = arrowprops, bbox = bbox, color = 'blue', size = 18)
    else:
        annotate_plot_line(ax, ser)

    ax.legend(loc='upper left')
    format_xaxis(ax, '%m-%d')
    ax.grid(which='both', axis = 'x')

    if traceback:
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

        start = pd.Period(traceback)
        rate = fits(ser, start)
        rate_index = ser[start:].index
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

        add_legend_entry(ax, line, "拟合数日增长倍数")

    if annotations:
        arrowprops=dict(facecolor='cyan', shrink=0.05)
        bbox=dict(facecolor='beige')
        for an in annotations:
            x = an['x']
            text = an['text']
            if fit_func:
                v0, v1 = ser[x], ser_fit[x] if x in ser_fit else 0
                y = v0 if v0 > v1 else v1
            else:
                y = ser[x]
            y0, y1 = ax.get_ylim()
            dy = (y1 - y0) * 0.04
            ax.annotate(text, xy =(x, y + dy), xytext = (0, 50), textcoords = 'offset points', arrowprops = arrowprops, bbox = bbox, ha = 'center')

    return ax
