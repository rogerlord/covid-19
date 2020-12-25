import datetime
import pandas as pd
from covid_19.nl.dataretrieval import get_cases_per_day_from_data_frame


def calculate_measure_historically(df_rivm_historical, measure, ggd_region=None):
    first_date = min(df_rivm_historical.index).date()
    last_date = max(df_rivm_historical.index).date()
    date_range = pd.date_range(start=first_date + datetime.timedelta(days=1), end=last_date)

    ds = pd.Series(index=date_range, dtype="float64")
    for dt in date_range:
        df_tminus1 = get_cases_per_day_from_data_frame(df_rivm_historical, dt - datetime.timedelta(days=1), ggd_region)
        df_t = get_cases_per_day_from_data_frame(df_rivm_historical, dt, ggd_region)
        ds[dt] = measure(df_t, df_tminus1)

    return ds
