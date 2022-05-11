from numpy import NaN
import pandas as pd
from glob import glob
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np

import datetime
from nsetools import Nse

STOCKS_WITH_CAP_INFO_PATH = "./data/stocks_list_with_cap_info.csv"


def _load_cap_info_df():
    df = pd.read_csv(STOCKS_WITH_CAP_INFO_PATH)
    return df

def _get_zip_dict_from_cap_info_df(col1, col2):
    df = _load_cap_info_df()
    stock_dict = dict(zip(df[col1], df[col2]))
    return stock_dict


def _get_stocks_list():
    nse = Nse()
    stocks_dict = nse.get_stock_codes()
    stocks_list = list(stocks_dict.keys())
    return stocks_list

@st.cache
def _convert_df(df):
   return df.to_csv().encode('utf-8')

def _append_nse(stocks):
    return [stock.upper() + ".NS" for stock in stocks]

def _get_years_ago_date(days_given):
    days = 1

    if "d" in days_given:
        days = int(days_given.replace("d", ""))
    elif "m" in days_given:
        days = int(days_given.replace("m", "")) * 30
    elif "y" in days_given:
        days = int(days_given.replace("y", "")) * 365
    st.write("Selected Days : " + str(days))
    n_years_ago = datetime.datetime.now() - datetime.timedelta(days=days)
    return n_years_ago.date()


def _get_family_stocks(family_name, stocks_dict, stocks_data):
    stocks = []

    for name, symbol in stocks_dict.items():
        if family_name.lower() in name.lower():
            if symbol.upper() == "ADANIGAS":
                stocks.append("ATGL")
            else:
                stocks.append(symbol)
    filter_df = stocks_data[stocks_data["Ticker"].isin(stocks)]
    return (stocks, filter_df)

@st.cache(show_spinner=False)
def _load_data(filepath):

    df = None
    with st.container():
        df = pd.read_csv(filepath)

    return df

def _load_data_without_cache(filepath):
    df = None
    with st.container():
        df = pd.read_csv(filepath)

    return df



def _process_data(
    df, col, if_dropna, if_remove_outliers, outlier_lower_qtl, outlier_upper_qtl
):
    if if_dropna:
        df = df.dropna(subset=[col])
    if if_remove_outliers:
        q_low = df[col].quantile(outlier_lower_qtl)
        q_hi = df[col].quantile(outlier_upper_qtl)
        df = df[(df[col] < q_hi) & (df[col] > q_low)]
    return df


def _get_specific_stocks(df, cap="LARGE_CAP", industry="IT"):
    filter_df = df.query(f" SubSector == '{industry}'")
    res_dict = dict(zip(filter_df.Ticker, filter_df["Name"]))
    return (res_dict, filter_df)




#move to proper loc


STOCKS_WITH_CAP_INFO_PATH = "./data/stocks_list_with_cap_info.csv"


def _load_cap_info_df():
    df = pd.read_csv(STOCKS_WITH_CAP_INFO_PATH)
    return df

def _get_zip_dict_from_cap_info_df(col1, col2):
    df = _load_cap_info_df()
    stock_dict = dict(zip(df[col1], df[col2]))
    return stock_dict


def _get_stocks_list():
    nse = Nse()
    stocks_dict = nse.get_stock_codes()
    stocks_list = list(stocks_dict.keys())
    return stocks_list



def get_stock_cap(stock):
    stock = stock.split(".")[0]
    cap_info = np.NaN
    SYMBOL_WITH_CAP_DICT = _get_zip_dict_from_cap_info_df("Symbol", "Capitalization")
    symbol_with_caps_list = list(SYMBOL_WITH_CAP_DICT.keys())

    if stock in symbol_with_caps_list:
        cap_info = SYMBOL_WITH_CAP_DICT[stock]

    return cap_info

def get_stock_industry(stock):
    stock = stock.split(".")[0]
    ind_info = np.NaN

    SYMBOL_WITH_INDUSTRY_DICT = _get_zip_dict_from_cap_info_df("Symbol", "Industry")
    symbol_with_industry_list = list(SYMBOL_WITH_INDUSTRY_DICT.keys())

    if stock in symbol_with_industry_list:
        ind_info = SYMBOL_WITH_INDUSTRY_DICT[stock]

    return ind_info


