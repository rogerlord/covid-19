from covid_19.nl.dataretrieval import get_latest_rivm_file, get_rivm_file, get_cases_per_day_from_data_frame, \
    get_rivm_file_historical, get_rivm_files_historical, get_cases_per_day_historical
import os
import datetime
import pytest
from pandas import Series


@pytest.fixture
def df_rivm_2020_07_24():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, 'fixtures/COVID-19_casus_landelijk_2020-07-24.csv')
    return get_rivm_file(file_name)


def test_get_rivm_file(df_rivm_2020_07_24):
    assertions_for_rivm_df(df_rivm_2020_07_24)


def test_get_rivm_file_historical(df_rivm_2020_07_24):
    df_rivm_historical = get_rivm_file_historical(datetime.date(2020, 7, 24))
    assert df_rivm_2020_07_24.equals(df_rivm_historical)


def test_get_rivm_files_historical():
    df_rivm_historical = get_rivm_files_historical(datetime.date(2020, 7, 24), datetime.date(2020, 7, 25))
    available_dates = df_rivm_historical.index.unique()
    assert len(available_dates) == 2
    for dt in available_dates:
        assert (dt.day == 24 or dt.day == 25) and dt.month == 7 and dt.year == 2020


def test_get_latest_rivm_file():
    assertions_for_rivm_df(get_latest_rivm_file())


def test_get_cases_per_day(df_rivm_2020_07_24):
    ds_cases_per_day = get_cases_per_day_from_data_frame(df_rivm_2020_07_24, datetime.date(2020, 7, 24))
    assert sum(ds_cases_per_day) == 52595


def test_get_cases_per_day_for_specific_ggd_region(df_rivm_2020_07_24):
    ds_cases_per_day = get_cases_per_day_from_data_frame(df_rivm_2020_07_24, datetime.date(2020, 7, 24), "GGD Amsterdam")
    assert sum(ds_cases_per_day) == 3518


def assertions_for_rivm_df(df):
    assert df.index.name == "Date_file"
    assert "Date_statistics" in df
    assert "Municipal_health_service" in df
    unique_types = df["Date_statistics_type"].unique()
    assert len(unique_types) == 3
    assert "DOO" in unique_types
    assert "DPL" in unique_types
    assert "DON" in unique_types


def test_get_cases_per_day_historical():
    cases_per_day_list = get_cases_per_day_historical(datetime.date(2020, 7, 24), datetime.date(2020, 7, 25))
    assert len(cases_per_day_list) == 2
    assert cases_per_day_list[0][0] == datetime.date(2020, 7, 24)
    assert isinstance(cases_per_day_list[0][1], Series)
    assert cases_per_day_list[1][0] == datetime.date(2020, 7, 25)
    assert isinstance(cases_per_day_list[1][1], Series)
