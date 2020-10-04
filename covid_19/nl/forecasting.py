import datetime
from covid_19.nl.dataretrieval import get_cases_per_day_from_file, get_lagged_values
import numpy as np
from numpy import linalg
from covid_19.pandasutils import filter_series
import math
import pandas as pd


def get_scaling_coefficient(lag, df_most_recent, df_lagged_values, first_date, last_date, beta=0.0):
    x = np.array(filter_series(df_lagged_values[str(lag)], first_date, last_date).sort_index().array)
    y = np.array(filter_series(df_most_recent, first_date, last_date).sort_index().array)
    w = np.array(list(reversed(list(map(lambda i: math.exp(-beta * i), range(len(x)))))))
    x = np.multiply(w, x)
    y = np.multiply(w, y)

    x = x[:, np.newaxis]

    scaling, _, _, _ = linalg.lstsq(x, y, rcond=None)
    return scaling[0]


def forecast_daily_cases(folder, beta=0.0):
    df_daily_cases = get_cases_per_day_from_file(folder).sort_index()
    df_lagged_values = get_lagged_values(folder).copy().sort_index()
    return forecast_daily_cases_from_data_frames(df_daily_cases, df_lagged_values, beta)


def forecast_daily_cases_from_data_frames(df_daily_cases, df_lagged_values, beta=0.0):
    df_daily_cases_forecast = df_daily_cases.copy()
    first_date = min(df_lagged_values.index).date()
    last_column = df_lagged_values.columns[-1]
    last_accurate_date = min(df_lagged_values[df_lagged_values[last_column].isna()].index - datetime.timedelta(days=1))
    last_accurate_date = last_accurate_date.date()

    for i in range(len(df_lagged_values.columns)):
        scaling = get_scaling_coefficient(i, df_daily_cases, df_lagged_values, first_date, last_accurate_date, beta)
        df_daily_cases_forecast.iloc[-(i+1)] = df_daily_cases_forecast.iloc[-(i+1)] * scaling
    return df_daily_cases_forecast


def recreate_lagged_values(df_lagged, dt: datetime.date):
    df = df_lagged.copy()
    first_date = min(df.index)
    df = df[first_date:dt]
    num_columns = len(df.columns)
    for i in range(1, num_columns):
        for j in range(i + 1, num_columns + 1):
            df.iat[-i, j - 1] = np.nan
    return df


def create_lagged_values_data_frame(cases_per_day_list, maximum_lag=np.inf):
    lagged_values_array = create_lagged_values_array(cases_per_day_list, maximum_lag)
    date_list = list(map(lambda x: x[0], cases_per_day_list))
    first_date = min(date_list)
    last_date = max(date_list)

    if maximum_lag is np.inf:
        maximum_lag = (last_date - first_date).days

    return pd.DataFrame(lagged_values_array, index=pd.date_range(
        start=first_date.strftime("%Y-%m-%d"),
        end=last_date.strftime("%Y-%m-%d")),
                      columns=list(range(maximum_lag+1)))


def create_lagged_values_array(cases_per_day_list, maximum_lag=np.inf):
    date_list = list(map(lambda x: x[0], cases_per_day_list))
    first_date = min(date_list)
    last_date = max(date_list)

    if maximum_lag is np.inf:
        maximum_lag = (last_date - first_date).days

    lagged_array = np.empty(((last_date - first_date).days + 1, maximum_lag + 1)) * np.nan
    for i in range((last_date - first_date).days + 1):
        df_cases_i = cases_per_day_list[i][1]
        for j in range(i + 1):
            dt_j = (first_date + datetime.timedelta(days=j)).strftime("%Y-%m-%d")
            if i-j > maximum_lag:
                continue

            if dt_j in df_cases_i.index:
                lagged_array[j, i-j] = df_cases_i[dt_j]
            else:
                lagged_array[j, i-j] = 0

    return lagged_array


def create_lagged_values_differences(lagged_array):
    num_rows = lagged_array.shape[0]
    num_cols = lagged_array.shape[1]

    differences_array = np.zeros((num_rows, num_cols))
    for i in range(0, num_rows):
        differences_array[i, 0] = lagged_array[i, 0]
        for j in range(1, num_cols):
            differences_array[i, j] = lagged_array[i, j] - lagged_array[i, j - 1]

    return differences_array
