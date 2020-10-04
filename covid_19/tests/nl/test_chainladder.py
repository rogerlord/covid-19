from covid_19.nl.chainladder import calculate_probabilities, calculate_log_likelihood, correct_daily_increments
import pytest
import numpy as np


def test_calculate_probabilities():
    probabilities = calculate_probabilities([0.25, 0.5])
    assert probabilities[0] == pytest.approx(0.723079666)
    assert probabilities[1] == pytest.approx(0.22366976)
    assert probabilities[2] == pytest.approx(1.0 - 0.723079666 - 0.22366976)


def test_calculate_log_likelihood():
    total_reported_numbers = [25, 14, 15, 75, 100]
    daily_increments = np.array([[10, 5, 0, 0, 0],
                                 [9, 4, 0, 0, np.nan],
                                 [12, 3, 0, np.nan, np.nan],
                                 [50, 20, np.nan, np.nan, np.nan],
                                 [100, np.nan, np.nan, np.nan, np.nan]])

    log_likelihood = calculate_log_likelihood(total_reported_numbers, daily_increments, [0.25, 0.5])
    assert log_likelihood == pytest.approx(-70.08175172)


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
