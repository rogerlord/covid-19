import pytest
import os
import pandas as pd
import datetime

from covid_19.nl.dataretrieval import get_rivm_files_historical, get_lagged_values, get_cases_per_day_from_data_frame
from covid_19.nl.forecasting import get_scaling_coefficient


@pytest.fixture
def covid_19_daily_cases():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, 'fixtures/COVID-19_daily_cases.csv')
    return pd.read_csv(file_name, squeeze=True, index_col=0, header=None, parse_dates=True)


@pytest.fixture
def covid_19_lagged_values():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, 'fixtures/COVID-19_lagged.csv')
    return pd.read_csv(file_name, index_col=0, header=0, parse_dates=True)


def test_get_scaling_coefficient(covid_19_daily_cases, covid_19_lagged_values):
    scaling = get_scaling_coefficient(0, covid_19_daily_cases, covid_19_lagged_values,
                                      datetime.date(2020, 7, 1), datetime.date(2020, 7, 26))
    assert scaling == pytest.approx(12.723, abs=1e-2)


def test_get_scaling_coefficient_different_lag(covid_19_daily_cases, covid_19_lagged_values):
    scaling = get_scaling_coefficient(5, covid_19_daily_cases, covid_19_lagged_values,
                                      datetime.date(2020, 7, 1), datetime.date(2020, 7, 26))
    assert scaling == pytest.approx(1.963, abs=1e-2)


def test_get_scaling_coefficient_with_exponential_weights(covid_19_daily_cases, covid_19_lagged_values):
    scaling = get_scaling_coefficient(0, covid_19_daily_cases, covid_19_lagged_values,
                                      datetime.date(2020, 7, 1), datetime.date(2020, 7, 26), beta=0.2)
    assert scaling == pytest.approx(15.519, abs=1e-2)


def test_get_scaling_coefficient_default_weight(covid_19_daily_cases, covid_19_lagged_values):
    scaling = get_scaling_coefficient(0, covid_19_daily_cases, covid_19_lagged_values,
                                      datetime.date(2020, 7, 1), datetime.date(2020, 7, 26))
    scaling_weight_specified = get_scaling_coefficient(0, covid_19_daily_cases, covid_19_lagged_values,
                                                       datetime.date(2020, 7, 1), datetime.date(2020, 7, 26), beta=0.0)
    assert scaling == pytest.approx(scaling_weight_specified)


def test_bla():
    df_rivm = get_rivm_files_historical(datetime.date(2020, 7, 1), datetime.date(2020, 7, 26))
    df_lagged = get_lagged_values(r"c:\projects\covid-19\\")

    df_daily = get_cases_per_day_from_data_frame(df_rivm, date_file=datetime.date(2020, 7, 14))

    forecast_daily_cases_from_data_frames()