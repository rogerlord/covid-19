from covid_19.nl.dataretrieval import get_latest_rivm_file, get_rivm_file
import os


def test_get_rivm_file():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, r".\fixtures\COVID-19_casus_landelijk_2020-07-24.csv")
    assertions_for_rivm_df(get_rivm_file(file_name))


def test_get_latest_rivm_file():
    assertions_for_rivm_df(get_latest_rivm_file())


def assertions_for_rivm_df(df):
    assert df.index.name == "Date_file"
    assert "Date_statistics" in df
    assert "Municipal_health_service" in df
    unique_types = df["Date_statistics_type"].unique()
    assert len(unique_types) == 3
    assert "DOO" in unique_types
    assert "DPL" in unique_types
    assert "DON" in unique_types

