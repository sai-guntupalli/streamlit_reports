import pandas as pd
from glob import glob
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

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

def _get_stock_symbols_from_holdings_csv(uploaded_file, vendor):
    stock_symbols = []
    if uploaded_file is not None and vendor is not None:
        if vendor == "Zerodha":
            with st.spinner("Loading Zerodha Holdings..."):
                df = pd.read_excel(uploaded_file, sheet_name="Equity")
            stock_symbols = list(df["Unnamed: 1"].dropna())[3:]
        elif vendor == "Custom":
            with st.spinner("Loading data..."):
                df = _load_data(uploaded_file)
            stock_symbols = list(df["Symbol"].dropna())
    else:
        st.error("Please Upload a Valid CSV file!")
    return stock_symbols

def _upload_data():
    with st.container():
        st.write("## Upload Data to get the Reports")
        # st.header("CSV Files")

    df = None
    vendor = "Zerodha"

    # Render file dropbox
    with st.expander("Upload data", expanded=True):
        how_to_load = st.selectbox(
            "How to access raw data? ", ("Zerodha", "Upstox", "Custom", "Sample data")
        )
        if how_to_load == "Zerodha":
            vendor = "Zerodha"

        elif how_to_load == "Upstox":
            vendor = "Upstox"

        elif how_to_load == "Custom":
            vendor = "Custom"

        elif how_to_load == "Sample data":
            vendor = "Sample"
            uploaded_file = "https://raw.githubusercontent.com/luxin-tian/mosco_ab_test/main/sample_data/cookie_cats.csv"

        if vendor != "Sample":
            uploaded_file = st.file_uploader("Choose a CSV file")
    st.write(vendor)
    stocks_list = _get_stock_symbols_from_holdings_csv(uploaded_file, vendor)
    st.write(stocks_list)
    return stocks_list
