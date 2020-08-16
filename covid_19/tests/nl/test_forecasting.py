import pytest
import os
import pandas as pd
import datetime

from covid_19.nl.dataretrieval import get_rivm_files_historical, get_lagged_values, get_cases_per_day_from_data_frame
from covid_19.nl.forecasting import get_scaling_coefficient, forecast_daily_cases_from_data_frames, recreate_lagged_values
from test_pandasutils import assert_frame_equal


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


def test_recreate_lagged_values(covid_19_lagged_values):
    current_path = os.path.dirname(os.path.realpath(__file__))
    df_lagged_most_recent = get_lagged_values(os.path.join(current_path, r"../../../"))
    df_lagged_recreated = recreate_lagged_values(df_lagged_most_recent, datetime.date(2020, 8, 8))
    assert_frame_equal(df_lagged_recreated, covid_19_lagged_values)


@pytest.mark.skip("Run manually")
def test_reperform_forecasting():
    first_date = datetime.date(2020, 7, 1)
    most_recent_date = datetime.date(2020, 8, 16)
    current_path = os.path.dirname(os.path.realpath(__file__))
    df_lagged_most_recent = get_lagged_values(os.path.join(current_path, r"../../../"))
    df_rivm = get_rivm_files_historical(first_date, most_recent_date)

    start_date = datetime.date(2020, 8, 1)
    end_date = most_recent_date
    for i in range(0, (end_date - start_date).days + 1):
        dt = start_date + datetime.timedelta(days=i)
        df_daily_cases = get_cases_per_day_from_data_frame(df_rivm, dt)
        df_lagged = recreate_lagged_values(df_lagged_most_recent, dt)
        df_lagged = df_lagged[first_date:dt]
        df_forecast = forecast_daily_cases_from_data_frames(df_daily_cases, df_lagged)
        df_forecast = df_forecast.rolling(window=7).mean().dropna()
        print(df_forecast.iloc[-1])
