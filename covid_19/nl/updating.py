import pandas as pd
import datetime
from covid_19.pandasutils import filter_series
from covid_19.nl.demography import get_ggd_regions
from covid_19.nl.dataretrieval import get_cases_per_day_from_file, get_latest_rivm_file, get_lagged_values, \
    get_cases_per_day_from_data_frame, get_rivm_file_historical
from covid_19.nl.measures import net_increases, gross_increases
from covid_19.nl.forecasting import forecast_daily_cases


def update_files(folder):
    ds_daily_cases = get_cases_per_day_from_file(folder)
    df_rivm = get_latest_rivm_file()
    last_available_date = max(ds_daily_cases.index).date()
    last_available_date_rivm = max(df_rivm.index).date()
    if not last_available_date_rivm > last_available_date:
        return

    ds_daily_cases_updated = get_cases_per_day_from_data_frame(df_rivm, last_available_date_rivm)
    ds_daily_cases_updated.sort_index(inplace=True)
    ds_daily_cases_updated.to_csv(folder + r"data\nl\COVID-19_daily_cases.csv", header=False)

    df_lagged = get_lagged_values(folder)
    last_contribution = filter_series(ds_daily_cases_updated, last_available_date_rivm, last_available_date_rivm)
    if len(last_contribution) == 0:
        print("Zero patients reported on {dt}".format(dt=last_available_date_rivm))
        last_contribution = 0
    elif len(last_contribution) > 1:
        raise Exception("More than one contribution on {dt}".format(dt=last_available_date_rivm))
    else:
        last_contribution = last_contribution.iloc[0]

    new_last_row = pd.Series(data=[last_contribution],
                             index=['0'],
                             name=datetime.datetime.combine(last_available_date_rivm, datetime.datetime.min.time()))
    df_lagged = df_lagged.append(new_last_row)
    for i in range(1, len(df_lagged.columns)):
        infection_date = last_available_date_rivm - datetime.timedelta(days=i)
        value_to_add = ds_daily_cases_updated[infection_date.strftime("%Y-%m-%d")]
        df_lagged.at[infection_date.strftime("%Y-%m-%d"), str(i)] = value_to_add
    df_lagged.to_csv(folder + r"data\nl\COVID-19_lagged.csv", header=True)


def update_measures(df_measures, folder):
    dt_last_measure_present = max(df_measures.index).date()
    df_rivm_latest = get_latest_rivm_file()
    dt_rivm_file = max(df_rivm_latest.index).date()

    if dt_last_measure_present == dt_rivm_file:
        return df_measures

    net_increases_21 = lambda df1, df2: net_increases(df1, df2, 21)
    gross_increases_21 = lambda df1, df2: gross_increases(df1, df2, 21)

    df_rivm_previous_day = get_rivm_file_historical(dt_rivm_file - datetime.timedelta(days=1))
    ggd_regions = get_ggd_regions()

    df_measures_updated = df_measures.copy()
    if dt_rivm_file in df_measures.index:
        return df_measures_updated

    new_row = pd.Series(dtype="float64")
    for ggd_region in ggd_regions["Municipal_health_service"]:
        new_row["net_" + ggd_region] = __calculate_measure(df_rivm_latest, df_rivm_previous_day, net_increases,
                                                           ggd_region)
        new_row["gross_" + ggd_region] = __calculate_measure(df_rivm_latest, df_rivm_previous_day, gross_increases,
                                                             ggd_region)
        new_row["net_21_" + ggd_region] = __calculate_measure(df_rivm_latest, df_rivm_previous_day,
                                                              net_increases_21, ggd_region)
        new_row["gross_21_" + ggd_region] = __calculate_measure(df_rivm_latest, df_rivm_previous_day,
                                                                gross_increases_21, ggd_region)

    new_row["net_nl"] = __calculate_measure(df_rivm_latest, df_rivm_previous_day, net_increases)
    new_row["gross_nl"] = __calculate_measure(df_rivm_latest, df_rivm_previous_day, gross_increases)
    new_row["net_21_nl"] = __calculate_measure(df_rivm_latest, df_rivm_previous_day, net_increases_21)
    new_row["gross_21_nl"] = __calculate_measure(df_rivm_latest, df_rivm_previous_day, gross_increases_21)

    nowcast_value = forecast_daily_cases(folder).rolling(window=7).mean().dropna().iloc[-1]
    new_row["nowcast_nl"] = nowcast_value

    new_row.name = dt_rivm_file
    df_measures_updated = df_measures_updated.append(new_row)
    df_measures_updated.index = pd.to_datetime(df_measures_updated.index, format="%Y-%m-%d")

    return df_measures_updated


def __calculate_measure(df_t, df_tminus1, measure, ggd_region=None):
    return measure(
        get_cases_per_day_from_data_frame(df_t, ggd_region=ggd_region),
        get_cases_per_day_from_data_frame(df_tminus1, ggd_region=ggd_region))
