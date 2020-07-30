import datetime
from covid_19.pandasutils import filter_data_frame
import pandas as pd
from covid_19.nl.dataretrieval import get_cases_per_day_from_data_frame


def net_increases(ds_t, ds_tminus1, number_of_observations=None):
    ds_diff = ds_t.sub(ds_tminus1, fill_value=0.0)
    if number_of_observations is None:
        return sum(ds_diff)

    last_available_date = max(ds_t.index)
    neglect_before_date = last_available_date - datetime.timedelta(days=number_of_observations-1)
    ds_diff_filtered = filter_data_frame(ds_diff, neglect_before_date, last_available_date)
    return sum(ds_diff_filtered.fillna(0.0))


def gross_increases(ds_t, ds_tminus1, number_of_observations=None):
    ds_diff = ds_t.sub(ds_tminus1, fill_value=0.0)
    if number_of_observations is None:
        return ds_diff.agg(lambda x: x[x > 0]).sum()

    last_available_date = max(ds_t.index)
    neglect_before_date = last_available_date - datetime.timedelta(days=number_of_observations-1)
    ds_diff_filtered = filter_data_frame(ds_diff, neglect_before_date, last_available_date)
    return ds_diff_filtered.agg(lambda x: x[x > 0]).sum()


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
