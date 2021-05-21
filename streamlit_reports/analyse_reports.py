import pandas as pd
from pandasgui import show

df = pd.read_csv(
    "reports\\stock_perf_reports\\2021-05-21\\new_stocks_perf_2021-05-21.csv"
)

print(df.head())

cols = [
    "symbol",
    "1d",
    "7d",
    "1m",
    "2m",
    "3m",
    "6m",
    "1y",
    "3y",
    "5y",
]


df = df[cols].sort_values(cols)


gui = show(df)
