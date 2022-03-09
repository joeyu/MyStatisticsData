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

def load_meta(meta_fp:str = 'meta.json'):
    with io.open(meta_fp, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return meta

def load_raw(raw_fp:str, meta_fn:str = 'meta.json'):
    """
    Loads raw data from all stored .csv files
    """

    meta = load_meta(meta_fn)
    meta_raw = meta['raw']
    #print(meta_raw)
    fp = Path(raw_fp)
    if fp.is_dir():
        fp_array = fp.glob('**/*.csv')
    elif fp.is_file():
        fp_array = [fp]

    combined_df = None
    df_array = []
    for fpath in fp_array:
        # if not '2021' in fpath.name:
        #    continue 
        print(fpath)
        df = pd.read_csv(fpath)
        if meta_raw['index_orientation'] == 1:
            # column
            new_col = [s.strip() for s in df.iloc[:,0]]

            data = []
            periods = []
            # row
            if 'year' in meta_raw['index_freq']:
                col_regex = '^' + meta_raw['columns']['Y'] + '$'
                col_regex = col_regex.replace('%Y', r'([12]\d{3})')
                for col in df:
                    m = re.match(col_regex, col) 
                    if m:
                        row_data = [i * meta_raw['unit'] for i in pd.to_numeric(df[col]).values]
                        data.append(row_data)
                        periods.append(m.groups()[0])
                        
            # Construct the DataFrame
            if data and periods:
                index = pd.PeriodIndex(periods, freq = 'A-DEC')
                df = pd.DataFrame(data, index = index, columns = new_col)

                # Append to the DataFrame array
                df_array.append(df)

    # Combine all the DataFrame array and sort ascendently
    combined_df = pd.concat(df_array)

    return combined_df.sort_index(axis = 0)

#Set font to support Chinese
mpl.rc('font', family = 'SimHei')

def plot_with_pct_change(df, title:str = None):

    if isinstance(df, pd.core.series.Series):
        df = pd.DataFrame(df)
        
    fig, axes = plt.subplots(len(df.columns), 1, sharex = True)
    if not isinstance(axes, np.ndarray): 
        axes = [axes]
    for i, col in enumerate(df.columns):
        ax = axes[i]
        ax.bar(df.index.strftime('%Y'), df[col])
        ax.set_ylabel(col + "（元）")

        pct = df[col].pct_change()
        pct = pct.apply(lambda x: x * 98)
        ax0 = ax.twinx()
        ax0.plot(df.index.strftime('%Y'), pct, color = "red")
        ax0.set_ylabel("Change%")

def data_and_pct_change(data):
    pct = data.pct_change()
    pct.name = "Change%"
    return pd.concat([data, pct], axis = 1)
