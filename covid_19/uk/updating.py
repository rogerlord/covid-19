import datetime

from covid_19.uk.dataretrieval import is_uk_gov_historical_file_present, UkGovRepository, REPORTING_LAG


def update_historical_files(folder, date_to_run=None):
    if date_to_run is None:
        date_to_run = datetime.datetime.today().date()

    reference_date = (date_to_run - datetime.timedelta(days=1))

    if is_uk_gov_historical_file_present(folder, reference_date):
        return

    repository = UkGovRepository(datetime.datetime.today().date(), set_index=False)
    df_uk_gov = repository.get_dataset(date_to_run)
    df_uk_gov.to_csv(r"{folder}\data\uk\historical\overview_{dt}.csv"
                     .format(folder=folder,
                             dt=reference_date.strftime("%Y-%m-%d")), index=False)


def update_files(folder, repository, date_to_run=None, start_from_scratch=False):
    update_historical_files(folder, date_to_run)
