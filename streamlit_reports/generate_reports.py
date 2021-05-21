from nsetools import Nse
import nsetools
import yfinance as yf
import ffn
import csv
from datetime import datetime
import time
import numpy as np


def get_stocks_list():
    nse = Nse()
    stocks_dict = nse.get_stock_codes()
    stocks_list = list(stocks_dict.keys())
    return stocks_list


def percentage_change(todays, nthday):
    return ((todays - nthday) / nthday) * 100


def get_past_price_performence(stocks_list, file_path, file_path_failed):
    performence_data = []
    failed_stocks = []
    fields = [
        "symbol",
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

    days_to_check = [
        1,
        2,
        3,
        4,
        5,
        6,
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
    for stock in stocks_list:
        try:
            if counter % 50 == 0:
                print("sleeping ...")
                time.sleep(10)

            print(f"Processing : {counter} - {stock}")
            stock_perf_list = []
            data = yf.download(
                stock + ".NS",
                period="max",
                threads=True,
            )

            data.sort_index(ascending=False, inplace=True)

            data_arr = data.to_numpy()
            # print(data_arr)
            data_arr_len = data_arr.shape[0]
            print(data_arr_len)

            todays_close = data_arr[0][4]
            # print("today")
            # print(todays_close)
            if todays_close > 25:
                for day in days_to_check:
                    if data_arr_len > day:
                        nth_day_close = data_arr[day][4]
                        # print(nth_day_close)
                        percent_change = percentage_change(todays_close, nth_day_close)
                    else:
                        percent_change = np.NaN

                    stock_perf_list.append(percent_change)

            if len(stock_perf_list) > 0:
                stock_perf_list.insert(0, stock)
                performence_data.append(stock_perf_list)

            counter += 1

        except Exception as e:
            print(f"Failed to get data for the stock : {stock}")
            print(e)
            failed_stocks.append(stock)
            counter += 1

    # print(performence_data)
    with open(
        file_path,
        "a",
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
    stocks_list = get_stocks_list()
    tdate = datetime.today().strftime("%Y-%m-%d")
    # date = d
    root_drive_path = "reports/stock_perf_reports"

    perf_report_path = root_drive_path + f"/{tdate}/new_stocks_perf_{tdate}.csv"
    failed_stocks_path = root_drive_path + f"/{tdate}/new_failed_stocks_{tdate}.csv"

    get_past_price_performence(stocks_list[1:], perf_report_path, failed_stocks_path)
