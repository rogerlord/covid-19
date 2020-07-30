from covid_19.nl.dataretrieval import get_latest_rivm_file, get_rivm_file, get_cases_per_day_from_data_frame
import os
import datetime


def test_get_rivm_file():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, r".\fixtures\COVID-19_casus_landelijk_2020-07-24.csv")
    assertions_for_rivm_df(get_rivm_file(file_name))


def test_get_latest_rivm_file():
    assertions_for_rivm_df(get_latest_rivm_file())


def test_get_cases_per_day():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, r".\fixtures\COVID-19_casus_landelijk_2020-07-24.csv")
    df_rivm = get_rivm_file(file_name)
    ds_cases_per_day = get_cases_per_day_from_data_frame(df_rivm, datetime.date(2020, 7, 24))
    assert sum(ds_cases_per_day) == 52595


def assertions_for_rivm_df(df):
    assert df.index.name == "Date_file"
    assert "Date_statistics" in df
    assert "Municipal_health_service" in df
    unique_types = df["Date_statistics_type"].unique()
    assert len(unique_types) == 3
    assert "DOO" in unique_types
    assert "DPL" in unique_types
    assert "DON" in unique_types
