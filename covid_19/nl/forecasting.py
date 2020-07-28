import datetime
from nl.dataretrieval import get_daily_cases, get_lagged_values, get_scaling_coefficient


def forecast_daily_cases(folder):
    df_daily_cases = get_daily_cases(folder).sort_index()
    df_daily_cases_forecast = df_daily_cases.copy()
    df_lagged_values = get_lagged_values(folder).copy().sort_index()
    first_date = min(df_lagged_values.index).date()
    last_date = max(df_lagged_values.index).date()
    last_accurate_date = last_date - datetime.timedelta(days=14)
    for i in range(len(df_lagged_values.columns)):
        scaling = get_scaling_coefficient(i, df_daily_cases, df_lagged_values, first_date, last_accurate_date)
        df_daily_cases_forecast.iloc[-(i+1)] = df_daily_cases_forecast.iloc[-(i+1)] * scaling
    return df_daily_cases_forecast
