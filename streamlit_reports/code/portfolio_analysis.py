import pandas as pd
from nsetools import Nse
import streamlit as st
from .utils import _load_data_without_cache , get_stock_cap, get_stock_industry

from st_aggrid import JsCode
from st_aggrid import AgGrid, GridOptionsBuilder

def _get_stock_symbols_from_holdings_csv(uploaded_file, vendor):
    stock_symbols = []
    df = pd.DataFrame()
    if uploaded_file is not None and vendor is not None:
        if vendor == "Zerodha Console":
            with st.spinner("Loading Zerodha Holdings..."):
                df = pd.read_excel(uploaded_file, sheet_name="Equity")
            # stock_symbols = list(df["Unnamed: 1"].dropna())[3:]
        else:
            with st.spinner("Loading data..."):
                df = _load_data_without_cache(uploaded_file)
            # stock_symbols = list(df["Symbol"].dropna())
    else:
        st.error("Please Upload a Valid CSV file!")
    return df

def _load_holdings_file():
    with st.container():
        st.write("## Upload Holdings file to Analyse.")
        # st.header("CSV Files")

    # Render file dropbox
    with st.expander("UPLOAD FILE", expanded=True):
        how_to_load = st.selectbox(
            "Choose the Holdings File Source? ", ("Zerodha Kite","Zerodha Console",  "Upstox", "Custom", "Sample data")
        )
        vendor = how_to_load
        
        if how_to_load == "Sample data":
            vendor = "Sample"
            uploaded_file = "https://raw.githubusercontent.com/luxin-tian/mosco_ab_test/main/sample_data/cookie_cats.csv"

        if vendor != "Sample":
            uploaded_file = st.file_uploader("Choose a CSV file")

    st.write(vendor)
    pdf = _get_stock_symbols_from_holdings_csv(uploaded_file, vendor)
    # st.write(stocks_list)
    return pdf

# @st.cache(allow_output_mutation=True)
def load_portfolio_data():
    portfolio_df = _load_holdings_file()
    df = portfolio_df.copy()
    #Instrument,Qty.,Avg. cost,LTP,Cur. val,P&L,Net chg.,Day chg.
    new_columns = ["Symbol", "Quantity", "ABP", "LTP", "Current Value", "P&L", "Net Change %", "Day Change"]


    if df.size >0:
        df.columns = new_columns

        df["Investment Value"] = round(df["Quantity"] * df["ABP"], 0)

        total_investment = df["Investment Value"].sum()
        # st.write(total_investment)
        df["Hold %"] = round((df["Investment Value"]/total_investment)*100, 2)

        df["Cap"] = df["Symbol"].apply(get_stock_cap)
        df["Industry"] = df["Symbol"].apply(get_stock_industry)


        order_cols = ["Symbol", "Cap", "Industry", "Quantity", "ABP", "Investment Value", "LTP", "Current Value", "P&L", "Net Change %", "Hold %"]

        df = df[order_cols]

        gb = GridOptionsBuilder.from_dataframe(df)

        cellRenderer1=JsCode('''function(params) {return '<a href="https://www.screener.in/company/' + params.value + '/consolidated/" target="_blank">'+ params.value+'</a>'}''')

        gb.configure_column("Symbol",
                            headerName="Symbol",
                            cellRenderer=cellRenderer1, checkboxSelection = True)

        

        selection_mode = 'multiple'

        # gb.configure_selection(selection_mode)
        gb.configure_selection(selection_mode, use_checkbox=True,rowMultiSelectWithClick = True,suppressRowClickSelection = False)
                # gb.configure_selection(selection_mode, use_checkbox=True, groupSelectsChildren=True, groupSelectsFiltered=True)


        # gb.configure_selection(selection_mode, use_checkbox=True, groupSelectsChildren=groupSelectsChildren, groupSelectsFiltered=groupSelectsFiltered)

        go  = gb.build()

        print(go)

        # go['rowSelection'] = "multiple"
        # go['rowMultiSelectWithClick'] = True
        # go['suppressRowClickSelection'] = False
        # go['groupSelectsChildren'] = False
        # go['groupSelectsFiltered'] = True


        grid_response = AgGrid(df,
            gridOptions=go, 
            width='100%',
            allow_unsafe_jscode=True)
        # fit_columns_on_grid_load=True)

        st.write(grid_response["data"])
        st.write(grid_response["selected_rows"])
    




