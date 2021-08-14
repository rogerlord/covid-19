import os
import pandas as pd
import datetime
import pytest
from covid_19.uk.updating import update_files
from covid_19.uk.dataretrieval import FileRepository, UkGovHistoricalRepository


@pytest.mark.skip("Only run manually")
def test_initialise_files():
    # Start with an initial COVID-19_lagged.csv file that is empty (just contains columns)
    current_path = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(current_path, r"../../../")

    repo = FileRepository(folder)

    update_files(folder, repo, date_to_run=datetime.date(2020, 8, 13), start_from_scratch=True)
    for dt in pd.date_range(start="2020-08-14", end="2021-01-10"):
        update_files(folder, repo, date_to_run=dt)


@pytest.mark.skip("Only run manually")
def test_retrieve_missing_file():
    repo = UkGovHistoricalRepository(False)
    date_to_run = datetime.date(2021, 6, 30)
    df = repo.get_dataset(date_to_run)
    folder = r"c:\\projects\\covid-19\\"
    df.to_csv(r"{folder}\data\uk\historical\overview_{dt}.csv"
              .format(folder=folder,
                      dt=(date_to_run - datetime.timedelta(days=1)).strftime("%Y-%m-%d")), index=False)
