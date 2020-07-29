import datetime
from covid_19.pandasutils import filter_data_frame


def net_increases(df_t, df_tminus1, number_of_observations=None):
    df_diff = (df_t.apply(len) - df_tminus1.apply(len)).sort_index()
    if number_of_observations is None:
        return sum(df_diff.fillna(0.0))

    last_available_date = max(df_t.index)
    neglect_before_date = last_available_date - datetime.timedelta(days=number_of_observations)
    df_diff_filtered = filter_data_frame(df_diff, neglect_before_date, last_available_date)
    return sum(df_diff_filtered.fillna(0.0))


def gross_increases(df_t, df_tminus1, number_of_observations=None):
    df_diff = (df_t.apply(len) - df_tminus1.apply(len)).sort_index()
    if number_of_observations is None:
        return sum(abs(df_diff.fillna).fillna(0.0))

    last_available_date = max(df_t.index)
    neglect_before_date = last_available_date - datetime.timedelta(days=number_of_observations)
    df_diff_filtered = filter_data_frame(df_diff, neglect_before_date, last_available_date)
    return sum(abs(df_diff_filtered.fillna(0.0)))
