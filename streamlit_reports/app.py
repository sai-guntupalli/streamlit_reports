"""Renders the Generate Stock Reports Dashboard web app. Made with Streamlit. 
"""
import os
from datetime import datetime
from plotly.express import data
import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats

# import plotly.express as px
import plotly.graph_objects as go

# import plotly.figure_factory as ff
import plotly.tools as tls
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt

import plotly.express as px

# Import the hypothesis_testing.py module
import streamlit_analytics

from streamlit_tags import st_tags
import datetime
import ffn

stocks_csv_path = "./data/stocks_list_with_cap_info.csv"
# stocks_csv_path = STOCKS_WITH_CAP_INFO_PATH

# st.set_option("deprecation.showPyplotGlobalUse", False)

COLUMNS_TO_DISPLAY_IN_REPORTS_DF = [
        "symbol",
        # "industry",
        # "cap",
        # "close_price",
        "1d",
        "2d",
        "3d",
        "4d",
        "5d",
        "6d",
        "7d",
        "1m",
        "2m",
        "3m",
        "4m",
        "5m",
        "6m",
        "7m",
        "8m",
        "9m",
        "10m",
        "11m",
        "1y",
        "3y",
        "5y",
    ]



def home(homepage_path, privacy_path, contact_path):
    """The home page."""
    with open(homepage_path, "r", encoding="utf-8") as homepage:
        homepage = homepage.read().split("---Insert video---")
        st.markdown(homepage[0], unsafe_allow_html=True)
        col1, col2 = st.beta_columns([1, 1])
        with col2:
            st.video("https://www.youtube.com/watch?v=zFMgpxG-chM")
        with col1:
            st.image(
                "https://images.ctfassets.net/zw48pl1isxmc/4QYN7VubAAgEAGs0EuWguw/165749ef2fa01c1c004b6a167fd27835/ab-testing.png",
                use_column_width="auto",
            )
            st.text("Image source: Optimizely")
        st.markdown(homepage[1], unsafe_allow_html=True)
    contact_us_ui(contact_path, if_home=True)
    with st.beta_expander(label="Privacy Notice"):
        with open(privacy_path, "r", encoding="utf-8") as privacy:
            st.markdown(privacy.read())


def contact_us_ui(contact_path, if_home=False):
    if not if_home:
        st.write("# New Features 💡")
        st.text_input("Send us suggestions", "Write something...")
        if_send = st.button("Send")
        if if_send:
            st.success("Thank you:) Your suggestions have been received. ")
            st.balloons()
    with open(contact_path, "r", encoding="utf-8") as contact:
        st.write(contact.read())


@st.cache(show_spinner=False)
def _load_data(filepath):

    df = None
    with st.beta_container():
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
    # filter_df = df[(df.Capitalization == cap ) (df.Industry == industry)]
    filter_df = df.query(f"Industry == '{industry}' &  Capitalization == '{cap}'")

    res_dict = dict(zip(filter_df.Symbol, filter_df["Company Name"]))
    return res_dict


def _append_nse(stocks):
    return [stock.upper() + ".NS" for stock in stocks]


def _upload_data():
    with st.beta_container():
        st.write("## Upload Data to get the Reports")
        # st.header("CSV Files")

    df = None
    vendor = "Zerodha"

    # Render file dropbox
    with st.beta_expander("Upload data", expanded=True):
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

    return stocks_list


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
        st.error("Please Enter a Valid CSV file!")

    return stock_symbols


def _get_years_ago_date(days_given):
    days = 1

    if "d" in days_given:
        days = int(days_given.replace("d", ""))
    elif "m" in days_given:
        days = int(days_given.replace("m", "")) * 30
    elif "y" in days_given:
        days = int(days_given.replace("y", "")) * 365

    st.write("Selected Days :")
    st.write(days)

    n_years_ago = datetime.datetime.now() - datetime.timedelta(days=days)
    return n_years_ago.date()


def _show_price_comparision_graph(data_df, rebase=False):

    min_date = data_df.index.min().date()
    max_date = data_df.index.max().date()

    layout_msg = f"Stocks Price comparision from {min_date} to {max_date}. ".title()

    if rebase:
        data_df = data_df.rebase()
        layout_msg = f"Stocks Price comparision from {min_date} to {max_date} with Price Rebased to 100.".title()

    traces = []

    for stock in list(data_df.columns):
        trace = go.Scatter(
            x=data_df.index,
            y=data_df[stock],
            mode="lines",
            name=stock.upper(),
        )
        traces.append(trace)

    layout = go.Layout(
        title=layout_msg,
        autosize=False,
        width=1000,
        height=600,
        # margin=go.layout.Margin(l=50, r=10, b=50, t=50, pad=4),
    )
    fig = go.Figure(data=traces, layout=layout)

    return fig


def stock_analysis():
    selected_stocks = []
    selected_stocks_nse = []

    with st.beta_container():
        st.title("Stock Analysis")
        st.info("You can get Analysis reports for Stocks here. ")

    stocks_df = _load_data(stocks_csv_path)
    st.write("Stock DF")
    st.write(stocks_df)

    available_caps = list(stocks_df["Capitalization"].unique())
    available_sectors = list(stocks_df["Industry"].unique())

    st.write("## How do you like to Analyze : ")
    way_of_analysis = st.radio(
        "",
        (
            "Analyse Stocks based on Sectors and Capitalization",
            "Analyse Custom Stocks",
            "Analyse Holdings",
        ),
    )

    # st.write(go_with_sectors)

    if way_of_analysis == "Analyse Stocks based on Sectors and Capitalization":

        st.write("## Select Market Capitalization : ")
        selected_cap = st.selectbox(
            "",
            options=available_caps,
            index=0,
        )

        st.write("## Select Sector : ")
        selected_sec = st.selectbox(
            "",
            options=available_sectors,
            index=0,
        )

        selected_stocks_dict = _get_specific_stocks(
            stocks_df, selected_cap, selected_sec
        )

        st.write(f"## Stocks avalable in {selected_cap} - {selected_sec} ")

        selected_stocks = list(selected_stocks_dict.keys())

        st.write(selected_stocks)

    elif way_of_analysis == "Analyse Custom Stocks":

        stock_symbols_dict = dict(zip(stocks_df["Company Name"], stocks_df["Symbol"]))

        selected_stocks_full_names = st_tags(
            label="## Select Stocks to Analyse:",
            # text="Press enter to add more",
            value=["Tata Consultancy Services Ltd.", "Wipro Ltd."],
            suggestions=list(stock_symbols_dict.keys()),
            maxtags=10,
            key="1",
        )

        selected_stocks = [
            stock_symbols_dict[key.title()] for key in selected_stocks_full_names
        ]

        st.write(selected_stocks)

    else:

        selected_stocks = _upload_data()

        st.write(selected_stocks)

    selected_stocks_nse = _append_nse(selected_stocks)

    st.write("## Select the Time Period : ")
    time_period = st.radio(
        "",
        (
            "1 Week",
            "1 Month",
            "3 Months",
            "6 Months",
            "1 Year",
            "3 Years",
            "5 Years",
            "10 Years",
        ),
    )

    time_period_dict = {
        "1 Week": "7d",
        "1 Month": "30d",
        "3 Months": "3m",
        "6 Months": "6m",
        "1 Year": "1y",
        "3 Years": "3y",
        "5 Years": "5y",
        "10 Years": "10y",
    }

    start_date = _get_years_ago_date(time_period_dict[time_period])

    data = ffn.get(selected_stocks_nse, start=str(start_date))
    data.columns = selected_stocks

    st.write(data)

    fig = _show_price_comparision_graph(data)
    st.write(fig)

    fig2 = _show_price_comparision_graph(data.rebase(), True)
    st.write(fig2)

def _get_latest_report_date():
    return "2021-05-21"


def sectoral_analysis():
    latest_report_date = _get_latest_report_date()
    report_path = f"./reports/stock_perf_reports/{latest_report_date}/stocks_perf_{latest_report_date}.csv"
    # streamlit_reports/streamlit_reports/reports/stock_perf_reports/2021-05-21/stocks_perf_2021-05-21.csv
    with st.beta_container():
        st.title(f"Daily Price Report- {latest_report_date}")
        st.info("Reports for price performence")


    df = _load_data(report_path)

    selected_columns = st_tags(
            label="### Select Columns to Display :",
            # text="Press enter to add more",
            value=COLUMNS_TO_DISPLAY_IN_REPORTS_DF,
            suggestions=COLUMNS_TO_DISPLAY_IN_REPORTS_DF,
            maxtags=30,
            key="1",
        )

    # st.table(df)
    df = df[selected_columns]
    st.dataframe(df, 2000, 1000)


def main():
    """Add control flows to organize the UI sections."""
    st.sidebar.image("./resources/logo.png", width=250)
    st.sidebar.write("")  # Line break
    st.sidebar.header("Navigation")
    side_menu_selectbox = st.sidebar.radio(
        "Menu",
        (
            "Home",
            "Stock Analysis",
            "Daily Price Change Report",
            "Custom Stocks Analysis",
            "Todays Report",
        ),
    )
    if side_menu_selectbox == "Home":
        home(
            homepage_path="./resources/homepage.md",
            privacy_path="./resources/privacy_notice.md",
            contact_path="./resources/contact_us.md",
        )
    elif side_menu_selectbox == "Custom Stocks Analysis":
        sub_menu_selectbox = st.sidebar.radio(
            "Data source", ("Upload CSV File", "Enter Manually")
        )
        if sub_menu_selectbox == "Upload CSV File":
            _upload_data()
        elif sub_menu_selectbox == "Enter Manually":
            _upload_data()
    elif side_menu_selectbox == "Todays Report":
        contact_us_ui(contact_path="./resources/contact_us.md")
    elif side_menu_selectbox == "Stock Analysis":
        stock_analysis()
    elif side_menu_selectbox == "Daily Price Change Report":
        sectoral_analysis()


if __name__ == "__main__":
    import os

    with streamlit_analytics.track("password"):
        st.set_page_config(
            page_title="Poneglyph - Stock Reports",
            page_icon="./resources/icon.png",
            layout="wide",
            initial_sidebar_state="auto",
        )
        try:
            main()
        except:
            st.error(
                "Oops! Something went wrong...Please check your input.\nIf you think there is a bug, please reach out. "
            )
            raise
