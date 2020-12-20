from covid_19.de.updating import update_files
from covid_19.de.dataretrieval import get_lagged_values, GitHubRepository, get_cases_per_day_from_data_frame
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

    update_files(folder, datetime.date(2020, 7, 1), True)
    for dt in pd.date_range(start="2020-07-02", end="2020-12-19"):
        update_files(folder, dt)


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
