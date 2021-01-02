import pandas as pd
import datetime
from covid_19.nl.demography import get_ggd_regions
from covid_19.nl.dataretrieval import get_cases_per_day_from_file, get_latest_rivm_file, get_lagged_values, \
    get_cases_per_day_from_data_frame, get_rivm_file_historical, RivmRepository, GitHubRepository
from covid_19.nl.forecasting import forecast_daily_cases
from covid_19 import chainladder
from covid_19.updating import update_lagged_values
from covid_19.measures import net_increases, gross_increases


def update_files(folder, repository, date_to_run=None):
    ds_daily_cases = get_cases_per_day_from_file(folder)

    if date_to_run is None:
        date_to_run = datetime.datetime.today().date()
    df_rivm = repository.get_dataset(date_to_run)

    last_available_date = max(ds_daily_cases.index).date()
    last_available_date_rivm = max(df_rivm.index).date()
    if not last_available_date_rivm > last_available_date:
        return

    ds_daily_cases_updated = get_cases_per_day_from_data_frame(df_rivm, last_available_date_rivm)
    ds_daily_cases_updated.sort_index(inplace=True)
    ds_daily_cases_updated.to_csv(folder + r"data\nl\COVID-19_daily_cases.csv", header=False)

    df_lagged = get_lagged_values(folder)
    df_lagged = update_lagged_values(df_lagged, ds_daily_cases_updated, last_available_date_rivm)

    df_lagged.to_csv(folder + r"data\nl\COVID-19_lagged.csv", header=True)


def update_measures(df_measures, folder, repository, date_to_run=None):
    dt_last_measure_present = df_measures.index[-1].date()

    if date_to_run is None:
        df_rivm_latest = repository.get_dataset(datetime.datetime.today().date())
    else:
        df_rivm_latest = repository.get_dataset(date_to_run)

    dt_rivm_file = max(df_rivm_latest.index).date()

    if dt_last_measure_present == dt_rivm_file:
        return df_measures

    df_rivm_previous_day = get_rivm_file_historical(dt_rivm_file - datetime.timedelta(days=1))
    ggd_regions = get_ggd_regions()

    df_measures_updated = df_measures.copy()
    new_row = pd.Series(dtype="float64")
    for ggd_region in ggd_regions["Municipal_health_service"]:
        new_row["net_" + ggd_region] = __calculate_measure(df_rivm_latest, df_rivm_previous_day, net_increases,
                                                           ggd_region)
        new_row["gross_" + ggd_region] = __calculate_measure(df_rivm_latest, df_rivm_previous_day, gross_increases,
                                                             ggd_region)

    new_row["net"] = __calculate_measure(df_rivm_latest, df_rivm_previous_day, net_increases)
    new_row["gross"] = __calculate_measure(df_rivm_latest, df_rivm_previous_day, gross_increases)

    nowcast_value = forecast_daily_cases(folder, maximum_lag=14).rolling(window=7).mean().dropna().iloc[-1]
    new_row["nowcast"] = nowcast_value

    nowcast_value_beta_0_2 = forecast_daily_cases(folder, beta=0.2, maximum_lag=14).rolling(window=7).mean().dropna().iloc[-1]
    new_row["nowcast_0_2"] = nowcast_value_beta_0_2

    get_lagged_values_func = lambda x: get_lagged_values(folder, x)
    method = "L-BFGS-B"

    corrected_cases_per_day, _ = chainladder.nowcast_cases_per_day(dt_rivm_file,
                                                                   get_lagged_values_func,
                                                                   get_cases_per_day_from_data_frame,
                                                                   repository, beta=0.0, method=method)
    nowcast_chainladder_value = pd.Series(corrected_cases_per_day).rolling(window=7).mean().dropna().iloc[-1]
    new_row["nowcast_chain"] = nowcast_chainladder_value

    corrected_cases_per_day, _ = chainladder.nowcast_cases_per_day(dt_rivm_file,
                                                                   get_lagged_values_func,
                                                                   get_cases_per_day_from_data_frame,
                                                                   repository, beta=0.2, method=method)
    nowcast_chainladder_value_beta_0_2 = pd.Series(corrected_cases_per_day).rolling(window=7).mean().dropna().iloc[-1]
    new_row["nowcast_chain_0_2"] = nowcast_chainladder_value_beta_0_2

    new_row.name = dt_rivm_file.strftime("%Y-%m-%d")
    df_measures_updated = df_measures_updated.append(new_row)
    df_measures_updated.index = pd.to_datetime(df_measures_updated.index, format="%Y-%m-%d")

    return df_measures_updated


def __calculate_measure(df_t, df_tminus1, measure, ggd_region=None):
    return measure(
        get_cases_per_day_from_data_frame(df_t, ggd_region=ggd_region),
        get_cases_per_day_from_data_frame(df_tminus1, ggd_region=ggd_region))
