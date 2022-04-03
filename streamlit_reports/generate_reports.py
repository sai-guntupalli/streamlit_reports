from nsetools import Nse
import nsetools
import yfinance as yf
import pathlib
import csv
from datetime import datetime, timedelta
import time
import numpy as np
import pandas as pd
from horology import Timing
import json

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



SYMBOL_WITH_CAP_DICT = _get_zip_dict_from_cap_info_df("Symbol", "Capitalization")
SYMBOL_WITH_INDUSTRY_DICT = _get_zip_dict_from_cap_info_df("Symbol", "Industry")

symbol_with_caps_list = list(SYMBOL_WITH_CAP_DICT.keys())
symbol_with_industry_list = list(SYMBOL_WITH_INDUSTRY_DICT.keys())


def percentage_change(todays, nthday):
    increase = todays - nthday
    return (increase / nthday) * 100


def get_nth_date_record(df, todays_date, nth_day):
    nth_day_date = todays_date - timedelta(nth_day)
    res_df  = pd.DataFrame()
    while res_df.empty:
        nth_day_weekdate = get_week_day(nth_day_date)
        res_df = df.query(f"Date == '{nth_day_weekdate}'")
        nth_day_date -= timedelta(1)
    res_df_arr = res_df.to_numpy()
    return (res_df_arr, nth_day_weekdate)

def get_week_day(input_date):
    while input_date.weekday() > 4: # Mon-Fri are 0-4
        input_date -= timedelta(days=1)
    return input_date


def get_past_price_performence(stocks_list, file_path, file_path_failed, dates_reference_path):
    performence_data = []
    failed_stocks = []
    fields = [
        "symbol",
        "industry",
        "cap",
        "close_price",
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

    days_to_check = [
        7,
        30,
        60,
        90,
        120,
        150,
        180,
        210,
        240,
        270,
        300,
        330,
        365,
        1095,
        1825,
    ]
    counter = 0
    dates_to_fetch = {}
    for stock in stocks_list:
        try:
            if counter % 50 == 0 and counter >0:
                print("sleeping ...")
                time.sleep(10)

            print(f"Processing : {counter} - {stock}")
            stock_perf_list = []
            data = yf.download(
                stock + ".NS",
                period="max",
                threads=True,
            )
            
            data.reset_index(inplace=True)
            data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
            data.sort_values('Date', ascending=False, inplace=True)


            data_arr = data.to_numpy()
            data_arr_len = data_arr.shape[0]
            print(f"Num of records : {data_arr_len}")

            todays_close = data_arr[0][4]
            todays_date_from_df = data_arr[0][0]

            if todays_close > 25:
                for day in days_to_check:
                    # print(f"calculating for the day : {day}")
                    if data_arr_len > day:
                        if day not in dates_to_fetch:
                            data_rec, date_fetched = get_nth_date_record(data, todays_date_from_df, day )
                            dates_to_fetch[day] = date_fetched
                        else:
                            data_rec= data.query(f"Date == '{dates_to_fetch[day]}'").to_numpy()
                    else:
                            percent_change = np.NaN

                    nth_day_close = data_rec[0][5]
                    percent_change = round(percentage_change(todays_close, nth_day_close), 1)
                    stock_perf_list.append(percent_change)

            if len(stock_perf_list) > 0:
                cap_info = np.NaN
                industry_info = np.NaN
                stock_perf_list.insert(0, stock)

                if stock in symbol_with_caps_list:
                    cap_info = SYMBOL_WITH_CAP_DICT[stock]

                if stock in symbol_with_industry_list:
                    industry_info = SYMBOL_WITH_INDUSTRY_DICT[stock]

                stock_perf_list.insert(1, industry_info)
                stock_perf_list.insert(2, cap_info)
                stock_perf_list.insert(3, round(todays_close, 1))

                performence_data.append(stock_perf_list)

            counter += 1

        except Exception as e:
            print(f"Failed to get data for the stock : {stock}")
            print(e)
            failed_stocks.append(stock)
            counter += 1
    

    formatted_dates_to_fetch = {key:str(value).split(" ")[0] for (key,value) in dates_to_fetch.items()}
    with open(dates_reference_path, 'w') as convert_file:
        convert_file.write(json.dumps(formatted_dates_to_fetch))


    # print(performence_data)
    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        # using csv.writer method from CSV package
        write = csv.writer(f)

        write.writerow(fields)
        write.writerows(performence_data)

    if len(failed_stocks) > 0:
        with open(file_path_failed, "w", newline="", encoding="utf-8") as f:
            write = csv.writer(f)

            write.writerow(["Symbol"])
            write.writerows([failed_stocks])


if __name__ == "__main__":
    import pathlib

    stocks_list = _get_stocks_list()
    tdate = str(datetime.today().strftime("%Y-%m-%d"))
    current_dir = pathlib.Path.cwd()
    # date = d
    root_drive_path = current_dir.joinpath("reports", "stock_perf_reports", tdate)

    pathlib.Path(root_drive_path).mkdir(parents=True, exist_ok=True)

    perf_report_path = root_drive_path.joinpath(f"stocks_perf_{tdate}.csv")
    failed_stocks_path = root_drive_path.joinpath(f"failed_stocks_{tdate}.csv")
    dates_reference_path = root_drive_path.joinpath(f"dates_reference_{tdate}.json")


    # stocks_anamoly = ["XPROINDIA", "TTML", "RAJMET", "JINDALPHOT", "DBREALTY"]

    with Timing(name='Time taken to generate the Report : ', unit='min'):
        get_past_price_performence(stocks_list[1:], perf_report_path, failed_stocks_path, dates_reference_path)

