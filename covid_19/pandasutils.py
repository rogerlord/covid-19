import datetime
import pandas as pd


def filter_data_frame(data_frame: pd.DataFrame, first_date: datetime.date,
                      last_date: datetime.date = None) -> pd.DataFrame:
    if last_date is None:
        return data_frame[first_date.strftime("%Y-%m-%d"):first_date.strftime("%Y-%m-%d")]
    return data_frame[first_date.strftime("%Y-%m-%d"):last_date.strftime("%Y-%m-%d")]


def filter_series(ds: pd.Series, first_date: datetime.date, last_date: datetime.date) -> pd.DataFrame:
    if not isinstance(first_date, datetime.datetime) and not isinstance(last_date, datetime.datetime):
        return ds[list(
            filter(lambda x: last_date + datetime.timedelta(days=1) > x > first_date - datetime.timedelta(days=1),
                   ds.index))]

    if ds.index.tz == first_date.tz and ds.index.tz == last_date.tz:
        return ds[list(
            filter(lambda x: last_date + datetime.timedelta(days=1) > x > first_date - datetime.timedelta(days=1),
                   ds.index))]

    if isinstance(first_date, datetime.datetime):
        if first_date.tzinfo != datetime.timezone.utc:
            first_date_utc = first_date.replace(tzinfo=datetime.timezone.utc)
            return filter_series(ds, first_date_utc, last_date)
    if isinstance(last_date, datetime.datetime):
        if last_date.tzinfo != datetime.timezone.utc:
            last_date_utc = last_date.replace(tzinfo=datetime.timezone.utc)
            return filter_series(ds, first_date, last_date_utc)
    if hasattr(ds.index.tz, 'zone'):
        if ds.index.tz.zone != "UTC":
            ds = ds.tz_localize(datetime.timezone.utc)

    return ds[list(
        filter(lambda x: last_date + datetime.timedelta(days=1) > x > first_date - datetime.timedelta(days=1),
               ds.index))]
