import pytest
from covid_19.nl.dataretrieval import get_rivm_file, get_cases_per_day_from_data_frame
from covid_19.nl.measures import net_increases, gross_increases
import os

from covid_19.nl.forecasting import forecast_daily_cases


@pytest.fixture
def covid_19_cases_2020_07_24():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, 'fixtures/COVID-19_casus_landelijk_2020-07-24.csv')
    return get_cases_per_day_from_data_frame(get_rivm_file(file_name))


@pytest.fixture
def covid_19_cases_2020_07_25():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, 'fixtures/COVID-19_casus_landelijk_2020-07-25.csv')
    return get_cases_per_day_from_data_frame(get_rivm_file(file_name))


def test_net_increases(covid_19_cases_2020_07_25, covid_19_cases_2020_07_24):
    assert net_increases(covid_19_cases_2020_07_25, covid_19_cases_2020_07_24) == 137


def test_net_increases_last_21_days(covid_19_cases_2020_07_25, covid_19_cases_2020_07_24):
    assert net_increases(covid_19_cases_2020_07_25, covid_19_cases_2020_07_24, 21) == 139


def test_gross_increases(covid_19_cases_2020_07_25, covid_19_cases_2020_07_24):
    assert gross_increases(covid_19_cases_2020_07_25, covid_19_cases_2020_07_24) == 144


def test_gross_increases_last_21_days(covid_19_cases_2020_07_25, covid_19_cases_2020_07_24):
    assert gross_increases(covid_19_cases_2020_07_25, covid_19_cases_2020_07_24, 21) == 141


@pytest.mark.skip("Only run locally")
def test_generate_nowcasts():
    current_path = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(current_path, r"../../../")
    df_updated = forecast_daily_cases(folder, beta=0.2, maximum_lag=14)
    data_forecast = df_updated.dropna()
    data_rolling = data_forecast.rolling(window=7).mean().dropna()
    data_rolling.to_csv("c:\\temp\\nowcasts.csv")
