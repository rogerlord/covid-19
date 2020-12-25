from covid_19.chainladder import nowcast_cases_per_day
from covid_19.de.dataretrieval import GitHubRepository, get_lagged_values, get_cases_per_day_from_data_frame, \
    RkiAndGitHubRepositoryWithCaching
import pytest
import pandas as pd
import os
import datetime


#@pytest.mark.skip("Only run locally")
def test_reperform_chainladder_nowcasts():
    current_path = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(current_path, r"../../../")

    today_date = datetime.date(2020, 12, 25)
    start_date = datetime.date(2020, 8, 1)
    end_date = datetime.date(2020, 12, 24)
    method = "L-BFGS-B"

    repo = RkiAndGitHubRepositoryWithCaching(today_date)

    get_lagged_values_func = lambda x: get_lagged_values(folder, x)

    for i in range(0, (end_date - start_date).days + 1):
        dt = start_date + datetime.timedelta(days=i)
        corrected_cases_per_day, probabilities = nowcast_cases_per_day(dt, get_lagged_values_func,
                                                                       get_cases_per_day_from_data_frame, repo, beta=0.2, method=method)
        avg_0_2 = pd.Series(corrected_cases_per_day).rolling(window=7).mean().dropna()

        corrected_cases_per_day, probabilities = nowcast_cases_per_day(dt, get_lagged_values_func,
                                                                       get_cases_per_day_from_data_frame, repo, beta=0.0, method=method)
        avg_0_0 = pd.Series(corrected_cases_per_day).rolling(window=7).mean().dropna()

        print("{zero},{zeropointtwo}".format(zero=avg_0_0.iloc[-1], zeropointtwo=avg_0_2.iloc[-1]))
        #print(avg.iloc[-1] - corrected_cases_per_day[-1]/7 + corrected_cases_per_day[-2]/7)
