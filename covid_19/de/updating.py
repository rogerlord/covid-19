import datetime
from covid_19.de.dataretrieval import get_cases_per_day_from_file, \
    get_latest_rki_file, get_rki_file_historical_from_github, get_cases_per_day_from_data_frame, \
    get_lagged_values, REPORTING_LAG
from covid_19.updating import update_lagged_values


def update_files(folder, date_to_run=None, start_from_scratch=False):
    if start_from_scratch:
        last_available_date = datetime.date.min
    else:
        ds_daily_cases = get_cases_per_day_from_file(folder)
        last_available_date = max(ds_daily_cases.index).date()

    last_available_date += datetime.timedelta(days=REPORTING_LAG)

    if date_to_run is None:
        df_rki = get_latest_rki_file()
    else:
        df_rki = get_rki_file_historical_from_github(date_to_run)

    last_available_date_rki = max(df_rki.index).date()
    if not last_available_date_rki > last_available_date:
        return

    ds_daily_cases_updated = get_cases_per_day_from_data_frame(df_rki, last_available_date_rki)
    ds_daily_cases_updated.sort_index(inplace=True)
    ds_daily_cases_updated.to_csv(folder + r"data\de\COVID-19_daily_cases.csv", header=False)

    df_lagged = get_lagged_values(folder)
    df_lagged = update_lagged_values(df_lagged, ds_daily_cases_updated, last_available_date_rki, REPORTING_LAG)

    df_lagged.to_csv(folder + r"data\de\COVID-19_lagged.csv", header=True)
