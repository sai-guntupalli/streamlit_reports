"""Renders the Generate Stock Reports Dashboard web app. Made with Streamlit. 
"""
from os import write
import streamlit as st
import pandas as pd
from glob import glob
import plotly.graph_objects as go
import streamlit_analytics
from streamlit_tags import st_tags
from nsetools import Nse
from st_aggrid import AgGrid

# import  code.utils
from code.portfolio_analysis import load_portfolio_data
from code.price_change_analysis import get_price_change_analysis
from code.stock_analysis import get_stock_analysis

# stocks_csv_path = "./data/nifty_450.csv"
# stocks_csv_path = "./data/stocks_list_with_cap_info.csv"
# stocks_csv_path = cu.STOCKS_WITH_CAP_INFO_PATH
# stocks_csv_path = cu.STOCKS_WITH_CAP_INFO_PATH


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
            "Portfolio Analysis"
            # "Todays Report",
        ),
    )
    if side_menu_selectbox == "Home":
        home(
            homepage_path="./resources/homepage.md",
            privacy_path="./resources/privacy_notice.md",
            contact_path="./resources/contact_us.md",
        )
    elif side_menu_selectbox == "Portfolio Analysis":
        sub_menu_selectbox = st.sidebar.radio(
            "Data source", ("Upload CSV File", "Enter Manually")
        )
        if sub_menu_selectbox == "Upload CSV File":
            load_portfolio_data()
        elif sub_menu_selectbox == "Enter Manually":
            # _upload_data()
            pass
    elif side_menu_selectbox == "Todays Report":
        # contact_us_ui(contact_path="./resources/contact_us.md")
        get_todays_report()
    elif side_menu_selectbox == "Stock Analysis":
        get_stock_analysis()
    elif side_menu_selectbox == "Daily Price Change Report":
        get_price_change_analysis()
    


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
