import datetime
import pandas as pd


def filter_data_frame(data_frame: pd.DataFrame, first_date: datetime.date, last_date: datetime.date = None) -> pd.DataFrame:
    if last_date is None:
        return data_frame[first_date.strftime("%Y-%m-%d"):first_date.strftime("%Y-%m-%d")]
    return data_frame[first_date.strftime("%Y-%m-%d"):last_date.strftime("%Y-%m-%d")]


def filter_series(ds: pd.Series, first_date: datetime.date, last_date: datetime.date) -> pd.DataFrame:
    first_date_utc = first_date.replace(tzinfo=datetime.timezone.utc)
    last_date_utc = last_date.replace(tzinfo=datetime.timezone.utc)
    return ds[list(filter(lambda x: last_date_utc + datetime.timedelta(days=1) > x > first_date_utc - datetime.timedelta(days=1), ds.index))]
