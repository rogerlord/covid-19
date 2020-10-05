import pytest
import os
import pandas as pd
import datetime

from covid_19.nl.dataretrieval import get_lagged_values, get_cases_per_day_historical
from covid_19.nl.forecasting import get_scaling_coefficient, forecast_daily_cases_from_data_frames
from covid_19.nl.manipulation import recreate_lagged_values


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


#@pytest.mark.skip("Run manually")
def test_reperform_forecasting():
    first_date = datetime.date(2020, 7, 1)
    most_recent_date = datetime.date(2020, 10, 5)
    beta = 0.2
    current_path = os.path.dirname(os.path.realpath(__file__))
    df_lagged_most_recent = get_lagged_values(os.path.join(current_path, r"../../../"), 14)
    cases_per_day_list = get_cases_per_day_historical(first_date, most_recent_date)

    start_date = datetime.date(2020, 8, 1)
    end_date = most_recent_date
    offset = (start_date - first_date).days
    for i in range(0, (end_date - start_date).days + 1):
        dt = start_date + datetime.timedelta(days=i)
        df_daily_cases = cases_per_day_list[offset + i][1]
        df_lagged = recreate_lagged_values(df_lagged_most_recent, dt)
        df_lagged = df_lagged[first_date:dt]
        df_forecast = forecast_daily_cases_from_data_frames(df_daily_cases, df_lagged, beta)
        avg = df_forecast.rolling(window=7).mean().dropna()
        print(avg.iloc[-1])
        #print(avg.iloc[-1] - df_forecast.iloc[-1]/7 + df_forecast.iloc[-2]/7)
