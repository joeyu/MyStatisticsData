import logging
import re
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from fontTools.ttLib import TTFont
import numpy as np
from pathlib import Path
import io
import json
from datetime import datetime

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
