from covid_19.dataretrieval import get_latest_rivm_file


def test_get_latest_rivm_file():
    df = get_latest_rivm_file()
    assert len(df) > 50000
