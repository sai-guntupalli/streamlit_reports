import pandas as pd
import nsetools

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


