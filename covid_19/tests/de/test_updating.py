from covid_19.de.updating import update_files, update_measures
from covid_19.de.dataretrieval import get_lagged_values, GitHubRepository, RkiAndGitHubRepositoryWithCaching,\
    get_cases_per_day_from_data_frame, get_measures
from covid_19 import chainladder
import os
import datetime
import pandas as pd
import pytest


@pytest.mark.skip("Only run manually")
def test_initialise_files():
    # Start with an initial COVID-19_lagged.csv file that is empty (just contains columns)
    current_path = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(current_path, r"../../../")

    repo = GitHubRepository()
    update_files(folder, repo, datetime.date(2020, 7, 1), True)
    for dt in pd.date_range(start="2020-07-02", end="2021-01-21"):
        update_files(folder, repo, date_to_run=dt)


@pytest.mark.skip("Only run manually")
def test_update_nowcasts():
    current_path = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(current_path, r"../../../")

    dt_rki_file = datetime.date(2020, 12, 19)
    rki_repository = GitHubRepository()

    get_lagged_values_func = lambda x: get_lagged_values(folder, x)

    corrected_cases_per_day, probs = chainladder.nowcast_cases_per_day(dt_rki_file,
                                                                   get_lagged_values_func,
                                                                   get_cases_per_day_from_data_frame,
                                                                   rki_repository, beta=0.2)

    probs = probs


@pytest.mark.skip("Only run manually")
def test_updating():
    current_path = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(current_path, r"../../../")

    dt_today = datetime.date(2021, 2, 7)

    repo = RkiAndGitHubRepositoryWithCaching(dt_today)

    start_date = datetime.date(2021, 1, 31)
    end_date = datetime.date(2021, 2, 6)

    for i in range(0, (end_date - start_date).days + 1):
        dt = start_date + datetime.timedelta(days=i)
        update_measures(get_measures(folder), folder, repo, dt).to_csv(folder + r"data\de\COVID-19_measures.csv")
