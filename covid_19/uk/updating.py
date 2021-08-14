import datetime

from covid_19.uk.dataretrieval import is_uk_gov_historical_file_present, UkGovRepository, REPORTING_LAG, \
    get_cases_per_day_from_file, get_cases_per_day_from_data_frame, get_lagged_values, PUBLICATION_LAG
from covid_19.updating import update_lagged_values


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
