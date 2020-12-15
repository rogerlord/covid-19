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
                      columns=list(range(maximum_lag)))


def create_lagged_values_array(cases_per_day_list, maximum_lag=np.inf):
    date_list = list(map(lambda x: x[0], cases_per_day_list))
    first_date = min(date_list)
    last_date = max(date_list)

    if maximum_lag is np.inf:
        maximum_lag = (last_date - first_date).days

    lagged_array = np.empty(((last_date - first_date).days + 1, maximum_lag)) * np.nan
    for i in range((last_date - first_date).days + 1):
        df_cases_i = cases_per_day_list[i][1]
        for j in range(i + 1):
            dt_j = (first_date + datetime.timedelta(days=j)).strftime("%Y-%m-%d")
            if i-j >= maximum_lag:
                continue

            if dt_j in df_cases_i.index:
                lagged_array[j, i-j] = df_cases_i[dt_j]
            else:
                lagged_array[j, i-j] = 0

    return lagged_array
