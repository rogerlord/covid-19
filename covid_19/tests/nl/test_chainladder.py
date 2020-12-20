from covid_19.chainladder import nowcast_cases_per_day
from covid_19.nl.dataretrieval import GitHubRepository, get_lagged_values, get_cases_per_day_from_data_frame
import pytest
import pandas as pd
import os
import datetime


@pytest.mark.skip("Only run locally")
def test_reperform_chainladder_nowcasts():
    current_path = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(current_path, r"../../../")

    start_date = datetime.date(2020, 8, 1)
    end_date = datetime.date(2020, 10, 10)
    beta = 0.2

    get_lagged_values_func = lambda x: get_lagged_values(folder, x)

    corrected_cases_per_day, probabilities = nowcast_cases_per_day(end_date, get_lagged_values_func,
                                                                   get_cases_per_day_from_data_frame, GitHubRepository(), beta=beta, method="L-BFGS-B")
    avg = pd.Series(corrected_cases_per_day).rolling(window=7).mean().dropna()
    avg.to_csv(r"c:\temp\chainladder.csv")

    for i in range(0, (end_date - start_date).days + 1):
        dt = start_date + datetime.timedelta(days=i)
        corrected_cases_per_day, probabilities = nowcast_cases_per_day(dt, get_lagged_values_func,
                                                                       get_cases_per_day_from_data_frame, GitHubRepository(), beta=beta, method="L-BFGS-B")
        avg = pd.Series(corrected_cases_per_day).rolling(window=7).mean().dropna()
        print(avg.iloc[-1])
        #print(avg.iloc[-1] - corrected_cases_per_day[-1]/7 + corrected_cases_per_day[-2]/7)
