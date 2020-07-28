import datetime
import pandas as pd


def filter_data_frame(data_frame: pd.DataFrame, requested_date: datetime.date) -> pd.DataFrame:
    return data_frame[requested_date.strftime("%Y-%m-%d"):requested_date.strftime("%Y-%m-%d")]


def filter_series(ds: pd.Series, first_date: datetime.date, last_date: datetime.date) -> pd.DataFrame:
    return ds[filter(lambda x: last_date + datetime.timedelta(days=1) > x > first_date - datetime.timedelta(days=1),
                     ds.index)]
