import datetime

from covid_19.de.dataretrieval import get_cases_per_day_from_file, \
    get_cases_per_day_from_data_frame, get_lagged_values, REPORTING_LAG
from covid_19.updating import update_lagged_values
import covid_19.chainladder as chainladder
from covid_19.measures import net_increases, gross_increases
import pandas as pd
from covid_19.dateutils import timer


@timer
def update_files(folder, repository, date_to_run=None, start_from_scratch=False):
    if start_from_scratch:
        last_available_date = datetime.date.min
    else:
        ds_daily_cases = get_cases_per_day_from_file(folder)
        last_available_date = max(ds_daily_cases.index).date()

    if date_to_run is None:
        date_to_run = datetime.datetime.today().date()
    df_rki = repository.get_dataset(date_to_run)

    last_available_date += datetime.timedelta(days=REPORTING_LAG)
    last_available_date_rki = df_rki.index.max().date()
    if not last_available_date_rki > last_available_date:
        return

    ds_daily_cases_updated = get_cases_per_day_from_data_frame(df_rki, last_available_date_rki)
    ds_daily_cases_updated.sort_index(inplace=True)
    ds_index = ds_daily_cases_updated.reset_index()["Refdatum"].apply(
        lambda x: datetime.datetime.combine(x.date(), datetime.datetime.min.time()))
    ds_daily_cases_updated = pd.Series(ds_daily_cases_updated.values, index=ds_index)
    ds_daily_cases_updated.to_csv(folder + r"data\de\COVID-19_daily_cases.csv", header=False, date_format="%Y-%m-%d")

    df_lagged = get_lagged_values(folder)
    df_lagged = update_lagged_values(df_lagged, ds_daily_cases_updated, last_available_date_rki, REPORTING_LAG)

    df_lagged.to_csv(folder + r"data\de\COVID-19_lagged.csv", header=True, date_format="%Y-%m-%d")


@timer
def update_measures(df_measures, folder, repository, date_to_run=None):
    if df_measures is None or len(df_measures.index) == 0:
        dt_last_measure_present = datetime.datetime.min
    else:
        dt_last_measure_present = df_measures.index[-1].date()

    if date_to_run is None:
        date_to_run = datetime.datetime.today().date()

    df_rki_latest = repository.get_dataset(date_to_run)
    dt_rki_file = max(df_rki_latest.index).date()

    if (dt_last_measure_present + datetime.timedelta(days=REPORTING_LAG)) == dt_rki_file:
        return df_measures

    df_rivm_previous_day = repository.get_dataset(dt_rki_file - datetime.timedelta(days=1))

    df_measures_updated = df_measures.copy()
    new_row = pd.Series(dtype="float64")
    new_row["net"] = __calculate_measure(df_rki_latest, df_rivm_previous_day, net_increases)
    new_row["gross"] = __calculate_measure(df_rki_latest, df_rivm_previous_day, gross_increases)

    get_lagged_values_func = lambda x: get_lagged_values(folder, x)
    method = "L-BFGS-B"

    corrected_cases_per_day, _ = chainladder.nowcast_cases_per_day(dt_rki_file,
                                                                   get_lagged_values_func,
                                                                   get_cases_per_day_from_data_frame,
                                                                   repository, beta=0.0, method=method,
                                                                   reporting_lag=REPORTING_LAG)
    nowcast_chainladder_value = pd.Series(corrected_cases_per_day).rolling(window=7).mean().dropna().iloc[-1]
    new_row["nowcast_chain"] = nowcast_chainladder_value

    corrected_cases_per_day, _ = chainladder.nowcast_cases_per_day(dt_rki_file,
                                                                   get_lagged_values_func,
                                                                   get_cases_per_day_from_data_frame,
                                                                   repository, beta=0.2, method=method,
                                                                   reporting_lag=REPORTING_LAG)
    nowcast_chainladder_value_beta_0_2 = pd.Series(corrected_cases_per_day).rolling(window=7).mean().dropna().iloc[-1]
    new_row["nowcast_chain_0_2"] = nowcast_chainladder_value_beta_0_2

    new_row.name = (dt_rki_file - datetime.timedelta(days=REPORTING_LAG)).strftime("%Y-%m-%d")
    df_measures_updated = df_measures_updated.append(new_row)
    df_measures_updated.index = pd.to_datetime(df_measures_updated.index, format="%Y-%m-%d")

    return df_measures_updated


def __calculate_measure(df_t, df_tminus1, measure):
    return measure(
        get_cases_per_day_from_data_frame(df_t),
        get_cases_per_day_from_data_frame(df_tminus1))
