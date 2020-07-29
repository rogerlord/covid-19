import pytest
from covid_19.nl.dataretrieval import get_rivm_file
from covid_19.nl.measures import net_increases
import os


#@pytest.fixture
def covid_19_cases_2020_07_24():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, 'fixtures/COVID-19_casus_landelijk_2020-07-24.csv')
    return get_rivm_file(file_name)


#@pytest.fixture
def covid_19_cases_2020_07_25():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, 'fixtures/COVID-19_casus_landelijk_2020-07-25.csv')
    return get_rivm_file(file_name)


@pytest.mark.skip("work in progress")
def test_net_increases():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, 'fixtures/COVID-19_casus_landelijk_2020-07-25.csv')
    df_1 = get_rivm_file(file_name)

    file_name = os.path.join(dir_path, 'fixtures/COVID-19_casus_landelijk_2020-07-24.csv')
    df_2 = get_rivm_file(file_name)

    assert net_increases(df_1["Date_statistics"], df_2["Date_statistics"]) == 137
