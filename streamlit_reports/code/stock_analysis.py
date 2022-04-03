from glob import glob
import streamlit as st

from streamlit_tags import st_tags
import ffn
from .graphs import _show_price_comparision_graph
from .utils import _upload_data, _append_nse, _get_years_ago_date, _get_family_stocks, _load_data, _get_specific_stocks


stocks_csv_path = "./data/nifty_450.csv"

def get_stock_analysis():
    selected_stocks = []
    selected_stocks_nse = []

    with st.container():
        st.title("Stock Analysis")
        st.info("You can get Analysis reports for Stocks here. ")

    stocks_df = _load_data(stocks_csv_path)
    st.write("Stock DF")
    st.write(stocks_df)
    # available_caps = list(stocks_df["Capitalization"].unique())
    available_sectors = list(stocks_df["SubSector"].unique())
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
        # st.write("## Select Market Capitalization : ")
        # selected_cap = st.selectbox(
        #     "",
        #     options=available_caps,
        #     index=0,
        # )
        st.write("## Select Sector : ")
        selected_sec = st.selectbox(
            "",
            options=available_sectors,
            index=0,
        )
        selected_stocks_dict, selected_stocks_df = _get_specific_stocks(
            stocks_df, None, selected_sec
        )

        st.write(f"## Stocks avalable in {selected_sec} ")
        selected_stocks = list(selected_stocks_dict.keys())
        st.write(
            selected_stocks_df[["Name", "Ticker", "ClosePrice", "MarketCap", "PERatio"]]
        )

    elif way_of_analysis == "Analyse Stock Familes":
        families = ["TATA", "ADANI", "BIRLA", "HDFC", "BAJAJ"]
        stock_symbols_dict = dict(zip(stocks_df["Name"], stocks_df["Ticker"]))
        st.write("## Select Family of the Stocks : ")
        selected_family = st.selectbox(
            "",
            options=families,
            index=0,
        )
        selected_stocks, filter_df = _get_family_stocks(
            selected_family, stock_symbols_dict, stocks_df
        )
        st.write("Selected Stocks : ")
        st.write(filter_df)

    elif way_of_analysis == "Analyse Custom Stocks":
        stock_symbols_dict = dict(zip(stocks_df["Name"], stocks_df["Ticker"]))
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

    display_price_graph = st.checkbox("Display Price Comparision Graph ?")

    if display_price_graph:

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
