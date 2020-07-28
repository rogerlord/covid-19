from covid_19.nl.dataretrieval import get_latest_rivm_file


def test_get_latest_rivm_file():
    df = get_latest_rivm_file()
    assert df.index.name == "Date_file"
    assert "Date_statistics" in df
    assert "Municipal_health_service" in df
    unique_types = df["Date_statistics_type"].unique()
    assert len(unique_types) == 3
    assert "DOO" in unique_types
    assert "DPL" in unique_types
    assert "DON" in unique_types

