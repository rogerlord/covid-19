from covid_19.nl.chainladder import calculate_probabilities, calculate_log_likelihood, correct_daily_increments, \
    correct_cases_per_day
import pytest
import numpy as np
import pandas as pd
import os
import datetime


def test_calculate_probabilities():
    probabilities = calculate_probabilities([0.25, 0.5])
    assert probabilities[0] == pytest.approx(0.723079666)
    assert probabilities[1] == pytest.approx(0.22366976)
    assert probabilities[2] == pytest.approx(1.0 - 0.723079666 - 0.22366976)


def test_calculate_log_likelihood():
    total_reported_numbers = [25, 14, 15, 70, 100]
    daily_increments = np.array([[10, 5, 10],
                                 [9, 4, 1],
                                 [12, 3, 1],
                                 [50, 20, np.nan],
                                 [100, np.nan, np.nan]])

    log_likelihood = calculate_log_likelihood(total_reported_numbers, daily_increments, [0.25, 0.5])
    assert log_likelihood == pytest.approx(-105.5483161)


def test_corrected_daily_increments():
    total_reported_numbers = [25, 14, 16, 70, 100]
    daily_increments = np.array([[10, 5],
                                 [9, 4],
                                 [12, 3],
                                 [50, 20],
                                 [100, np.nan]])

    corrected_daily_increments = correct_daily_increments(total_reported_numbers, daily_increments, 2)
    row_sum = np.nansum(corrected_daily_increments, axis=1)
    assert (row_sum == total_reported_numbers).all()


@pytest.mark.skip("Only run locally")
def test_optimise():
    current_path = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(current_path, r"../../../")

    start_date = datetime.date(2020, 8, 1)
    end_date = datetime.date(2020, 10, 5)
    for i in range(0, (end_date - start_date).days + 1):
        dt = start_date + datetime.timedelta(days=i)
        corrected_cases_per_day, probabilities = correct_cases_per_day(dt, folder)
        avg = pd.Series(corrected_cases_per_day).rolling(window=7).mean().dropna()
        print(avg.iloc[-1])
        #print(avg.iloc[-1] - corrected_cases_per_day[-1]/7 + corrected_cases_per_day[-2]/7)
