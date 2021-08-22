import datetime

from covid_19.uk.dataretrieval import is_uk_gov_historical_file_present, UkGovRepository, REPORTING_LAG, \
    get_cases_per_day_from_file, get_cases_per_day_from_data_frame, get_lagged_values, PUBLICATION_LAG
from covid_19.updating import update_lagged_values
from covid_19.dateutils import timer
import covid_19.chainladder as chainladder
from covid_19.measures import net_increases, gross_increases
import pandas as pd


def update_historical_files(folder, date_to_run=None):
    if date_to_run is None:
        date_to_run = datetime.datetime.today().date()

    reference_date = (date_to_run - datetime.timedelta(days=PUBLICATION_LAG))

    if is_uk_gov_historical_file_present(folder, reference_date):
        return

    repository = UkGovRepository(datetime.datetime.today().date(), set_index=False)
    df_uk_gov = repository.get_dataset(date_to_run)
    df_uk_gov.to_csv(r"{folder}\data\uk\historical\overview_{dt}.csv"
                     .format(folder=folder,
                             dt=reference_date.strftime("%Y-%m-%d")), index=False)


def update_files(folder, repository, date_to_run=None, start_from_scratch=False):
    update_historical_files(folder, date_to_run)

    if start_from_scratch:
        last_available_date = datetime.date.min
    else:
        ds_daily_cases = get_cases_per_day_from_file(folder)
        last_available_date = max(ds_daily_cases.index).date()

    if date_to_run is None:
        date_to_run = datetime.datetime.today().date()
    df_uk_gov = repository.get_dataset(date_to_run)

    last_available_date_uk_gov = max(df_uk_gov.index).date()
    if not last_available_date_uk_gov > last_available_date:
        return

    ds_daily_cases_updated = get_cases_per_day_from_data_frame(df_uk_gov, last_available_date_uk_gov)
    ds_daily_cases_updated.sort_index(inplace=True)
    ds_daily_cases_updated.to_csv(folder + r"data\uk\COVID-19_daily_cases.csv", header=False)

    df_lagged = get_lagged_values(folder)
    df_lagged = update_lagged_values(df_lagged, ds_daily_cases_updated, last_available_date_uk_gov, REPORTING_LAG)

    df_lagged.to_csv(folder + r"data\uk\COVID-19_lagged.csv", header=True)


@timer
def update_measures(df_measures, folder, repository, date_to_run=None):
    if df_measures is None or len(df_measures.index) == 0:
        dt_last_measure_present = datetime.datetime.min
    else:
        dt_last_measure_present = df_measures.index[-1].date()

    if date_to_run is None:
        date_to_run = datetime.datetime.today().date()

    df_latest = repository.get_dataset(date_to_run)
    dt_file = max(df_latest.index).date()

    if (dt_last_measure_present + datetime.timedelta(days=REPORTING_LAG)) == dt_file:
        return df_measures

    df_previous_day = repository.get_dataset(date_to_run - datetime.timedelta(days=1))

    df_measures_updated = df_measures.copy()
    new_row = pd.Series(dtype="float64")
    new_row["net"] = __calculate_measure(df_latest, df_previous_day, net_increases)
    new_row["gross"] = __calculate_measure(df_latest, df_previous_day, gross_increases)

    get_lagged_values_func = lambda x: get_lagged_values(folder, x)
    method = "L-BFGS-B"

    corrected_cases_per_day, _ = chainladder.nowcast_cases_per_day(date_to_run,
                                                                   get_lagged_values_func,
                                                                   get_cases_per_day_from_data_frame,
                                                                   repository, beta=0.0, method=method,
                                                                   reporting_lag=REPORTING_LAG,
                                                                   publication_lag=PUBLICATION_LAG)
    nowcast_chainladder_value = pd.Series(corrected_cases_per_day).rolling(window=7).mean().dropna().iloc[-1]
    new_row["nowcast_chain"] = nowcast_chainladder_value

    corrected_cases_per_day, _ = chainladder.nowcast_cases_per_day(date_to_run,
                                                                   get_lagged_values_func,
                                                                   get_cases_per_day_from_data_frame,
                                                                   repository, beta=0.2, method=method,
                                                                   reporting_lag=REPORTING_LAG,
                                                                   publication_lag=PUBLICATION_LAG)
    nowcast_chainladder_value_beta_0_2 = pd.Series(corrected_cases_per_day).rolling(window=7).mean().dropna().iloc[-1]
    new_row["nowcast_chain_0_2"] = nowcast_chainladder_value_beta_0_2

    new_row.name = (dt_file - datetime.timedelta(days=REPORTING_LAG)).strftime("%Y-%m-%d")
    df_measures_updated = df_measures_updated.append(new_row)
    df_measures_updated.index = pd.to_datetime(df_measures_updated.index, format="%Y-%m-%d")

    return df_measures_updated


def __calculate_measure(df_t, df_tminus1, measure):
    return measure(
        get_cases_per_day_from_data_frame(df_t),
        get_cases_per_day_from_data_frame(df_tminus1))
