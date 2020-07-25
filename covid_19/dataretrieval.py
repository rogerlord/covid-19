import pandas as pd
import datetime
import numpy as np
from numpy import linalg


def get_latest_rivm_file():
    url = "https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.csv"
    df_rivm = pd.read_csv(url, sep=";")
    df_rivm["Date_file"] = pd.to_datetime(df_rivm["Date_file"], format='%Y-%m-%d')
    df_rivm["Date_statistics"] = pd.to_datetime(df_rivm["Date_statistics"], format='%Y-%m-%d')
    df_rivm.set_index("Date_file", inplace=True)
    return df_rivm


def get_daily_cases(folder):
    return pd.read_csv(folder + r"data\COVID-19_daily_cases.csv", squeeze=True, index_col=0, header=None, parse_dates=True)


def get_lagged_values(folder):
    return pd.read_csv(folder + r"data\COVID-19_lagged.csv", index_col=0, header=0, parse_dates=True)


def get_values_on_date(data_frame, requested_date):
    requested_date_datetime = datetime.datetime.combine(requested_date, datetime.datetime.min.time())
    requested_date_datetime_next_day = requested_date_datetime + datetime.timedelta(days=1)
    return data_frame[requested_date_datetime:requested_date_datetime_next_day]


def filter_dataseries(ds, first_date, last_date):
    return ds[filter(lambda x: last_date + datetime.timedelta(days=1) > x > first_date - datetime.timedelta(days=1),
                     ds.index)]


def get_scaling_coefficient(lag, df_most_recent, df_lagged_values, first_date, last_date):
    x = np.array(filter_dataseries(df_lagged_values[str(lag)], first_date, last_date).sort_index().array)
    y = np.array(filter_dataseries(df_most_recent, first_date, last_date).sort_index().array)
    x = x[:, np.newaxis]

    scaling, _, _, _ = linalg.lstsq(x, y, rcond=None)
    return scaling[0]


def update_daily_cases_with_forecasts(folder):
    df_daily_cases = get_daily_cases(folder).sort_index()
    df_daily_cases_updated = df_daily_cases.copy()
    df_lagged_values = get_lagged_values(folder).copy().sort_index()
    first_date = min(df_lagged_values.index).date()
    last_date = max(df_lagged_values.index).date()
    last_accurate_date = last_date - datetime.timedelta(days=14)
    for i in range(len(df_lagged_values.columns)):
        scaling = get_scaling_coefficient(i, df_daily_cases, df_lagged_values, first_date, last_accurate_date)
        df_daily_cases_updated.iloc[-(i+1)] = df_daily_cases_updated.iloc[-(i+1)] * scaling
    return df_daily_cases_updated


def update_files(folder):
    df_daily_cases = get_daily_cases(folder)
    df_rivm = get_latest_rivm_file()
    last_available_date = max(df_daily_cases.index).date()
    last_available_date_rivm = max(df_rivm.index).date()
    if not last_available_date_rivm > last_available_date:
        return

    df_daily_cases_updated = get_values_on_date(df_rivm, last_available_date_rivm)["Date_statistics"].value_counts()
    df_daily_cases_updated.sort_index(inplace=True)
    df_daily_cases_updated.to_csv(folder + r"data\COVID-19_daily_cases.csv", header=False)

    df_lagged = get_lagged_values(folder)
    new_last_row = pd.Series(data=[df_daily_cases_updated[last_available_date_rivm]],
                             index=['0'],
                             name=datetime.datetime.combine(last_available_date_rivm, datetime.datetime.min.time()))
    df_lagged = df_lagged.append(new_last_row)
    for i in range(1, len(df_lagged.columns)):
        infection_date = last_available_date_rivm - datetime.timedelta(days=i)
        value_to_add = df_daily_cases_updated[infection_date]
        df_lagged.at[infection_date, str(i)] = value_to_add
    df_lagged.to_csv(folder + r"data\COVID-19_lagged.csv", header=True)
