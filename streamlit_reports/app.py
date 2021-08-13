"""Renders the Generate Stock Reports Dashboard web app. Made with Streamlit. 
"""
from datetime import datetime
from os import write
from plotly.express import data
import streamlit as st
import pandas as pd
from glob import glob
import plotly.graph_objects as go
import pathlib
import ffn
import streamlit_analytics
from streamlit_tags import st_tags
import datetime
from nsetools import Nse

stocks_csv_path = "./data/stocks_list_with_cap_info.csv"
# stocks_csv_path = cu.STOCKS_WITH_CAP_INFO_PATH

COLUMNS_TO_DISPLAY_IN_REPORTS_DF = [
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
        homepage = homepage.read()
    st.markdown(homepage, unsafe_allow_html=True)
    contact_us_ui(contact_path, if_home=True)
    with st.expander(label="Privacy Notice"):
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
    filter_df = df.query(f"Industry == '{industry}' &  Capitalization == '{cap}'")
    res_dict = dict(zip(filter_df.Symbol, filter_df["Company Name"]))
    return res_dict


def _append_nse(stocks):
    return [stock.upper() + ".NS" for stock in stocks]


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
    st.write("Selected Days : " + str(days))
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
        autosize=True,
        width=1600,
        height=800,
        # margin=go.layout.Margin(l=50, r=10, b=50, t=50, pad=4),
    )
    fig = go.Figure(data=traces, layout=layout)
    return fig


def stock_analysis():
    selected_stocks = []
    selected_stocks_nse = []

    with st.container():
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
            "Analyse Stock Familes",
            "Analyse Custom Stocks",
            "Analyse Holdings",
        ),
    )

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

    elif way_of_analysis == "Analyse Stock Familes":
        families = ["TATA", "ADANI", "BIRLA", "HDFC", "BAJAJ"]
        stock_symbols_dict = dict(zip(stocks_df["Company Name"], stocks_df["Symbol"]))
        st.write("## Select Family of the Stocks : ")
        selected_family = st.selectbox(
            "",
            options=families,
            index=0,
        )
        selected_stocks = _get_family_stocks(selected_family, stock_symbols_dict)
        st.write("Selected Stocks : ")
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
        index=4,
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

    display_df = st.checkbox("Display Obtained Data ?")

    if display_df:
        st.write(data)

    fig = _show_price_comparision_graph(data)
    st.write(fig)

    fig2 = _show_price_comparision_graph(data.rebase(), True)
    st.write(fig2)


def _get_family_stocks(family_name, stocks_dict):
    stocks = []

    for name, symbol in stocks_dict.items():
        if family_name.lower() in name.lower():
            if symbol.upper() == "ADANIGAS":
                stocks.append("ATGL")
            else:
                stocks.append(symbol)
    return stocks


def _get_latest_report_date():
    current_dir = pathlib.Path.cwd()
    root_path = current_dir.joinpath("reports", "stock_perf_reports")
    res = []
    for path in root_path.iterdir():
        if path.is_dir():
            res.append(path.name)
    res.sort()
    return res[-1]


def _apply_link_to_stock(stock):
    base_url = f"""https://www.gateway-tt.in/trade?orderConfig=%5B%7B%22quantity%22%3A10%2C%22ticker%22%3A%22{stock}%22%7D%5D&cardsize=big&withSearch=true&withTT=true"""
    return base_url


def _add_tickertape_url_to_df(df):
    df["Link"] = _apply_link_to_stock(df["symbol"])

    return df


def get_todays_report():
    req_cols = [
        "symbol",
        "ltp",
        "previousPrice",
        "netPrice",
        "tradedQuantity",
        "turnoverInLakhs",
    ]
    nse = Nse()
    st.markdown("## Todays Top Gainers and Top Loosers")
    st.write("")
    st.markdown("## Todays Top Gainers :")
    top_gainers = nse.get_top_gainers()
    gainer_df = pd.DataFrame(top_gainers)
    # req_cols = gainer_df[req_cols]
    st.write(gainer_df[req_cols])

    st.markdown("## Todays Top Loosers :")
    top_loosers = nse.get_top_losers()
    looser_df = pd.DataFrame(top_loosers)
    looser_df_rounded = looser_df.round(decimals=1)
    # req_cols = looser_df_rounded.columns[:-2]
    st.write(looser_df_rounded[req_cols])

    # udf = _add_tickertape_url_to_df(looser_df_rounded)
    # looser_df_rounded["Link"] = looser_df_rounded["symbol"].apply(_apply_link_to_stock)
    # st.write(looser_df_rounded.to_html(escape=False), unsafe_allow_html=True)
    # pass


def sectoral_analysis():
    latest_report_date = _get_latest_report_date()
    # print(latest_report_date)
    current_dir = pathlib.Path.cwd()
    # date = d
    report_path = current_dir.joinpath(
        "reports",
        "stock_perf_reports",
        latest_report_date,
        f"stocks_perf_{latest_report_date}.csv",
    )

    with st.container():
        st.title(f"Daily Returns Report - {latest_report_date}")
        st.info("Reports for price performence")

    df = _load_data(report_path)

    industries = list(df["industry"].unique())[1:]
    industries.insert(0, "All Industries")

    caps = list(df["cap"].unique())[1:]
    caps.insert(0, "All Caps")
    st.write("### Select the Industry : ")
    industry = st.selectbox("", industries, index=0)

    if industry != "All Industries":
        df = df[df["industry"] == industry]

    st.write("### Select the Cap : ")
    cap = st.selectbox("", caps, index=0)

    if cap != "All Caps":
        df = df[df["cap"] == cap]

    selected_columns = st_tags(
        label="### Select Columns to Display :",
        # text="Press enter to add more",
        value=COLUMNS_TO_DISPLAY_IN_REPORTS_DF,
        suggestions=COLUMNS_TO_DISPLAY_IN_REPORTS_DF,
        maxtags=30,
        key="1",
    )
    common_cols = [
        "symbol",
        "industry",
        "cap",
        "close_price",
    ]

    df = df[common_cols + selected_columns]
    selected_stocks = list(df["symbol"])
    st.dataframe(df, 2000, 1000)
    display_graphs = st.checkbox("Display Price Charts ?")
    if display_graphs:
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
            index=4,
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
        display_df = st.checkbox("Display Obtained Data ?")
        if display_df:
            st.write(data)
        fig = _show_price_comparision_graph(data)
        st.write(fig)
        fig2 = _show_price_comparision_graph(data.rebase(), True)
        st.write(fig2)


def main():
    """Add control flows to organize the UI sections."""
    # st.sidebar.image("./resources/logo.png", width=250)
    st.sidebar.header("Ponyglyph")
    st.sidebar.write("")  # Line break
    # st.sidebar.header("Navigation")
    side_menu_selectbox = st.sidebar.radio(
        "Menu",
        (
            "Home",
            "Todays Report",
            "Stock Analysis",
            "Daily Price Change Report",
            "Custom Stocks Analysis",
            # "Todays Report",
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
        # contact_us_ui(contact_path="./resources/contact_us.md")
        get_todays_report()
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
