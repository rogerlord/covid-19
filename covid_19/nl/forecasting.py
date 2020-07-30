import datetime
from covid_19.nl.dataretrieval import get_cases_per_day_from_file, get_lagged_values
import numpy as np
from numpy import linalg
from covid_19.pandasutils import filter_series


def get_scaling_coefficient(lag, df_most_recent, df_lagged_values, first_date, last_date):
    x = np.array(filter_series(df_lagged_values[str(lag)], first_date, last_date).sort_index().array)
    y = np.array(filter_series(df_most_recent, first_date, last_date).sort_index().array)
    x = x[:, np.newaxis]

    scaling, _, _, _ = linalg.lstsq(x, y, rcond=None)
    return scaling[0]


def forecast_daily_cases(folder):
    df_daily_cases = get_cases_per_day_from_file(folder).sort_index()
    df_daily_cases_forecast = df_daily_cases.copy()
    df_lagged_values = get_lagged_values(folder).copy().sort_index()
    first_date = min(df_lagged_values.index).date()
    last_date = max(df_lagged_values.index).date()
    last_accurate_date = last_date - datetime.timedelta(days=14)
    for i in range(len(df_lagged_values.columns)):
        scaling = get_scaling_coefficient(i, df_daily_cases, df_lagged_values, first_date, last_accurate_date)
        df_daily_cases_forecast.iloc[-(i+1)] = df_daily_cases_forecast.iloc[-(i+1)] * scaling
    return df_daily_cases_forecast
