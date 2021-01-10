import time
import datetime
from covid_19.uk.dataretrieval import UkGovHistoricalRepository, get_uk_gov_dataframe_from_file, \
    get_cases_per_day_from_data_frame
import pytest
import os


@pytest.mark.skip("Run manually to backfill archive")
def test_get_uk_files():
    # Data obtained from https://coronavirus.data.gov.uk/details/download
    start_date = datetime.date(2020, 8, 12)
    end_date = datetime.date(2020, 8, 13)
    repo = UkGovHistoricalRepository(False)

    current_folder = os.path.dirname(os.path.realpath(__file__))
    target_folder = os.path.join(current_folder, '../../../data/uk/historical/')

    for i in range((end_date - start_date).days + 1):
        dt = start_date + datetime.timedelta(days=i)
        df_uk_gov = repo.get_dataset(dt)
        df_uk_gov.to_csv(r"{target_folder}\overview_{dt}.csv"
                         .format(target_folder=target_folder,
                                 dt=dt.strftime("%Y-%m-%d")), index=False)
        time.sleep(40)


def test_get_uk_gov_dataframe_from_file():
    current_folder = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(current_folder, '../../../')

    df_uk_gov = get_uk_gov_dataframe_from_file(folder, datetime.date(2021, 1, 9))
    assert df_uk_gov.index.unique()[0].date() == datetime.date(2021, 1, 9)
    assert df_uk_gov["date"].max() == datetime.date(2021, 1, 9)
