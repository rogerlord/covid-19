from covid_19.chainladder import calculate_probabilities, calculate_log_likelihood, correct_daily_increments, \
    nowcast_cases_per_day, calculate_log_likelihood_jacobian, calculate_log_likelihood_jacobian_probabilities, \
    calculate_log_likelihood_with_probability_parameters, calculate_log_likelihood_jacobian_probabilities_without_last, \
    calculate_delta_parameters_from_probabilities, generate_equal_probabilities, generate_decaying_probabilities
from covid_19.nl.dataretrieval import get_rivm_file, get_lagged_values, get_cases_per_day_from_data_frame
import pytest
from pytest import approx
import numpy as np
import os
import datetime


def test_calculate_probabilities():
    probabilities = calculate_probabilities([0.25, 0.5])
    assert probabilities[0] == pytest.approx(0.723079666)
    assert probabilities[1] == pytest.approx(0.22366976)
    assert probabilities[2] == pytest.approx(1.0 - 0.723079666 - 0.22366976)


def test_calculate_deltas_from_probabilities():
    probabilities = [0.2, 0.2, 0.2, 0.2, 0.2]
    deltas = calculate_delta_parameters_from_probabilities(probabilities)
    assert deltas[0] == pytest.approx(-1.49994, abs=1e-5)
    assert deltas[1] == pytest.approx(-1.2459, abs=1e-5)
    assert deltas[2] == pytest.approx(-0.90272, abs=1e-5)
    assert deltas[3] == pytest.approx(-0.36651, abs=1e-5)


def test_equal_probabilities():
    probabilities = generate_equal_probabilities(5)
    for p in probabilities:
        assert p == pytest.approx(0.2, abs=1e-10)


def test_decaying_probabilities():
    probabilities = generate_decaying_probabilities(0.3, 5)
    assert probabilities[0] == pytest.approx(0.701706, abs=1e-5)
    assert probabilities[1] == pytest.approx(0.210512, abs=1e-5)
    assert probabilities[2] == pytest.approx(0.063154, abs=1e-5)
    assert probabilities[3] == pytest.approx(0.018946, abs=1e-5)
    assert probabilities[4] == pytest.approx(0.005684, abs=1e-5)


def test_calculate_log_likelihood():
    total_reported_numbers = [25, 14, 15, 70, 100]
    daily_increments = np.array([[10, 5, 10],
                                 [9, 4, 1],
                                 [12, 3, 1],
                                 [50, 20, np.nan],
                                 [100, np.nan, np.nan]])

    log_likelihood = calculate_log_likelihood(total_reported_numbers, daily_increments, [0.25, 0.5])
    assert log_likelihood == pytest.approx(-105.5483161)


class TestCase1:
    total_reported_numbers = [25, 14, 15, 70, 100]
    daily_increments = np.array([[10, 5, 10],
                                 [9, 4, 1],
                                 [12, 3, 1],
                                 [50, 20, np.nan],
                                 [100, np.nan, np.nan]])
    delta_parameters = [0.25, 0.5]


class TestCase2:
    total_reported_numbers = [25, 14, 15, 70, 100, 150, 175]
    daily_increments = np.array([[10, 4, 10, 1],
                                 [9, 3, 1, 1],
                                 [12, 3, 1, -1],
                                 [50, 15, 2, 1],
                                 [100, 0.0, 0.0, np.nan],
                                 [125, 20, np.nan, np.nan],
                                 [140, np.nan, np.nan, np.nan]])

    delta_parameters = [0.25, 0.5, 0.4]


@pytest.mark.parametrize("beta", [0.0, 0.1, 0.2])
@pytest.mark.parametrize("test_case", [TestCase1(), TestCase2()])
def test_calculate_log_likelihood_jacobian_probabilities(beta, test_case):
    probabilities = calculate_probabilities(test_case.delta_parameters)
    jacobian = calculate_log_likelihood_jacobian_probabilities(test_case.total_reported_numbers, test_case.daily_increments, probabilities)
    delta_tester(func=lambda x: calculate_log_likelihood_with_probability_parameters(test_case.total_reported_numbers, test_case.daily_increments, x),
                 x=probabilities,
                 bump_size=1.0e-8,
                 tolerance=1.0e-6,
                 expected_deltas=jacobian)


@pytest.mark.parametrize("beta", [0.0, 0.1, 0.2])
@pytest.mark.parametrize("test_case", [TestCase1(), TestCase2()])
def test_calculate_log_likelihood_jacobian_probabilities_without_last(beta, test_case):
    probabilities = calculate_probabilities(test_case.delta_parameters)
    jacobian = calculate_log_likelihood_jacobian_probabilities_without_last(test_case.total_reported_numbers, test_case.daily_increments, probabilities)

    def log_likelihood(probabilities_without_last):
        p = probabilities_without_last.copy()
        p.append(1.0 - sum(p))
        return calculate_log_likelihood_with_probability_parameters(test_case.total_reported_numbers, test_case.daily_increments, p)

    delta_tester(func=lambda x: log_likelihood(x),
                 x=probabilities[:-1],
                 bump_size=1.0e-8,
                 tolerance=1.0e-6,
                 expected_deltas=jacobian)


@pytest.mark.parametrize("beta", [0.0, 0.1, 0.2])
@pytest.mark.parametrize("test_case", [TestCase1(), TestCase2()])
def test_calculate_log_likelihood_jacobian(beta, test_case):
    jacobian = calculate_log_likelihood_jacobian(test_case.total_reported_numbers, test_case.daily_increments, test_case.delta_parameters)

    def log_likelihood(deltas):
        return calculate_log_likelihood(test_case.total_reported_numbers, test_case.daily_increments, deltas)

    delta_tester(func=lambda x: log_likelihood(x),
                 x=test_case.delta_parameters,
                 bump_size=1.0e-8,
                 tolerance=1.0e-6,
                 expected_deltas=jacobian)


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


class FixtureRepository:
    def __init__(self, folder):
        self.folder = folder

    @staticmethod
    def get_dataset(dt: datetime.date):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_name = os.path.join(dir_path, 'nl/fixtures/COVID-19_casus_landelijk_' + dt.isoformat() + '.csv')
        return get_rivm_file(file_name)


@pytest.mark.skip("Fix later")
def test_nowcast_powell_vs_lbfgsb():
    dt = datetime.date(2020, 10, 1)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(dir_path, '../../')

    get_lagged_values_func = lambda x: get_lagged_values(folder, x)

    corrected_cases_per_day_powell, probabilities_powell =\
        nowcast_cases_per_day(dt, get_lagged_values_func, get_cases_per_day_from_data_frame,  FixtureRepository, 31, beta=0.0, method="Powell")
    corrected_cases_per_day_lbfgsb, probabilities_lbfgsb =\
        nowcast_cases_per_day(dt, get_lagged_values_func, get_cases_per_day_from_data_frame, FixtureRepository, 31, beta=0.0, method="L-BFGS-B")

    max_probability_difference = max(abs(np.array(probabilities_powell) - np.array(probabilities_lbfgsb)))
    assert max_probability_difference < 0.0003

    corrected_cases_differences = max(abs(np.array(corrected_cases_per_day_powell) - np.array(corrected_cases_per_day_lbfgsb)))
    assert corrected_cases_differences < 5.0


def delta_tester(func, x, bump_size, tolerance, expected_deltas):
    for i in range(len(x)):
        x_up = x.copy()
        x_up[i] += bump_size
        func_up = func(x_up)

        x_down = x.copy()
        x_down[i] -= bump_size
        func_down = func(x_down)

        func_delta_approx = (func_up - func_down) / (2.0 * bump_size)
        assert func_delta_approx == approx(expected_deltas[i], tolerance, tolerance)
