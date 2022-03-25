import pandas as pd
import matplotlib
import matplotlib.cm as cm
from .constant import *

def get_period_data(df, st, ed):
    st = (pd.to_datetime(st) - pd.Timestamp('2000-01-01')).days
    ed = (pd.to_datetime(ed) - pd.Timestamp('2000-01-01')).days
    res = df.loc[(df["date_value"]>=st)&(df["date_value"]<=ed)]
    return res

def group_by_time(df, date_col="date", period="D", fun="mean", agg = None, groupby=None):
    """this function will handle grouping date (and also other columns) of a df

    Args:
        df (_type_): df of data
        date_col (str, optional): datetime like column.
        period (str, optional): group to H, D, W, M, Q, Y.
        fun (str, optional): aggregating function, sum, mean, std, max, min.
        groupby (_type_, optional): other groups.

    Returns:
        res: grouped df
            "period" column can use as plotting label, 
            "date_value" column can use as regression value, 
        df: original df
    """
    
    if groupby is None:
        groupby=[]
    df["period"] = pd.to_datetime(df[date_col]).dt.to_period(period) 
    if agg is None:
        res = df.groupby(["period"] + groupby).apply(fun).reset_index()
    else:
        res = df.groupby(["period"] + groupby).agg(**agg).reset_index()
    res["date"] = res["period"].dt.start_time
    res["date_value"] =  (pd.to_datetime(res["date"]) - pd.Timestamp('2000-01-01')).dt.total_seconds()
    
    df = df.drop(columns=["period"])
    
    return res, df

def period_diff(df, period_1, period_2, excluding=None, including=None):
    # calculate value difference between two period in one df
    if excluding is not None:
        df = df.loc[:, ~df.columns.isin(excluding)]
    if including is not None:
        df = df[including]
    
    df_1 = get_period_data(df, period_1[0], period_1[1])
    df_2 = get_period_data(df, period_2[0], period_2[1])
    mm = min(df_1.shape[0], df_2.shape[0])
    res = df_1.iloc[:mm,] - df_2.iloc[:mm,].values
    res = res.loc[:, ~res.columns.isin(["date_value"])]
    
    return res

def color_map(df, column, cm_dict):
    minima = min(df[column])
    maxima = max(df[column])

    norm = matplotlib.colors.Normalize(vmin=minima, vmax=maxima, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm_dict[column])
    c = mapper.to_rgba(df[column],alpha=0.5)
    colors = []
    for cc in c:
        colors.append(matplotlib.colors.to_hex(cc, keep_alpha=True))

    df["color"] = colors
    
    return df


def color_map2(df, column, cm_dict):
    df["max_key"] = df[RATIO_KEYS].idxmax(axis=1)
    for k in RATIO_KEYS:
        minima = min(df[k])
        maxima = max(df[k])

        norm = matplotlib.colors.Normalize(vmin=minima, vmax=maxima, clip=True)
        mapper = cm.ScalarMappable(norm=norm, cmap=cm_dict[k])
        c = mapper.to_rgba(df[k],alpha=0.5)
        colors = []
        for cc in c:
            colors.append(matplotlib.colors.to_hex(cc, keep_alpha=True))

        df[k+"_color"] = colors
    
    if column =="all":
        colors = []
        for row in df.iterrows():
            r = row[1]
            max_key = r["max_key"]
            colors.append(r[max_key+"_color"])
        df["color"] = colors
    else:
        df["color"] = df[column+"_color"]
        
    return df