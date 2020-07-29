import datetime
import pandas as pd


def filter_data_frame(data_frame: pd.DataFrame, first_date: datetime.date, last_date: datetime.date = None) -> pd.DataFrame:
    if last_date is None:
        return data_frame[first_date.strftime("%Y-%m-%d"):first_date.strftime("%Y-%m-%d")]
    return data_frame[first_date.strftime("%Y-%m-%d"):last_date.strftime("%Y-%m-%d")]


def filter_series(ds: pd.Series, first_date: datetime.date, last_date: datetime.date) -> pd.DataFrame:
    return ds[filter(lambda x: last_date + datetime.timedelta(days=1) > x > first_date - datetime.timedelta(days=1),
                     ds.index)]
