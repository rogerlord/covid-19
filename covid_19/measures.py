import datetime
from pandasutils import filter_data_frame


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
