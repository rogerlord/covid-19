import numpy as np
import pandas as pd
import datetime


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


def recreate_lagged_values(df_lagged, dt: datetime.date):
    df = df_lagged.copy()
    first_date = min(df.index)
    df = df[first_date:dt]
    num_columns = len(df.columns)
    for i in range(1, num_columns):
        for j in range(i + 1, num_columns + 1):
            df.iat[-i, j - 1] = np.nan
    return df
