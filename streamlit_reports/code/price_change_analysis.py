from glob import glob
import plotly.graph_objects as go
import pathlib
import streamlit as st
import pandas as pd

from streamlit_tags import st_tags
from st_aggrid import JsCode

from nsetools import Nse
from st_aggrid import AgGrid, GridOptionsBuilder
import ffn
from .utils import _append_nse, _get_years_ago_date, _load_data, _convert_df
from .graphs import _show_price_comparision_graph


COLUMNS_TO_DISPLAY_IN_REPORTS_DF = [
    "7d",
    "1m",
    "2m",
    "3m",
    "4m",
    "5m",
    "6m",
    "1y",
    "3y",
    "5y",
]


def _get_latest_report_date():
    current_dir = pathlib.Path.cwd()
    root_path = current_dir.joinpath("reports", "stock_perf_reports")
    res = []
    for path in root_path.iterdir():
        if path.is_dir():
            res.append(path.name)
    res.sort()
    return res[-1]

# @st.cache(allow_output_mutation=True)
def get_price_change_analysis():
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
    # st.dataframe(df.style.format({'close_price': '{:.1f}', '7d': '{:.1f}', '1m': '{:.1f}', '2m': '{:.1f}', '3m': '{:.1f}', '4m': '{:.1f}', '5m': '{:.1f}', '6m': '{:.1f}', '1y': '{:.1f}', '3y': '{:.1f}', '5y': '{:.1f}'}))
    
    gb = GridOptionsBuilder.from_dataframe(df)

    cellRenderer1=JsCode('''function(params) {return '<a href="https://www.screener.in/company/' + params.value + '/consolidated/" target="_blank">'+ params.value+'</a>'}''')

    gb.configure_column("symbol",
                            headerName="symbol",
                            cellRenderer=cellRenderer1, checkboxSelection = True)

    go  = gb.build()

    go['rowSelection'] = "multiple"
    go['rowMultiSelectWithClick'] = True
    go['suppressRowClickSelection'] = False
    go['groupSelectsFiltered'] = True

    # print(go)


    grid_response = AgGrid(df, gridOptions=go, allow_unsafe_jscode=True,)
    # selected_rows = user_selected_df["data"]

    csv = _convert_df(df)

    st.download_button(
   "Press to Download",
   csv,
   "file.csv",
   "text/csv",
   key='download-csv'
)

    # st.subheader("Returned grid data:") 
    #returning as HTML table bc streamlit has issues when rendering dataframes with timedeltas:
    # https://github.com/streamlit/streamlit/issues/3781
    # st.markdown(grid_response['data'].to_html(), unsafe_allow_html=True)

    st.subheader("grid selection:")
    st.write(grid_response['selected_rows'])

    # st.write("Filtered Df")

    # st.write(selected_rows)


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
