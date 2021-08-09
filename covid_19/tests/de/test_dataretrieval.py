import os
import datetime
import pytest
from covid_19.de.dataretrieval import get_latest_rki_file, get_rki_file_historical_from_CharlesStr, \
    get_rki_file_historical_from_ihucos, get_rki_data_frame, get_rki_file_historical_from_github, \
    get_rki_file_historical_from_micb25, get_cases_per_day_from_data_frame, LocalCacheRepository


@pytest.fixture
def df_rki_2020_07_24():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, 'fixtures/RKI_COVID19_2020-07-24.csv')
    return get_rki_data_frame(file_name)


#
#
# def test_get_rivm_file(df_rivm_2020_07_24):
#     assertions_for_rivm_df(df_rivm_2020_07_24)
#
#
# def test_get_rivm_file_historical(df_rivm_2020_07_24):
#     df_rivm_historical = get_rivm_file_historical(datetime.date(2020, 7, 24))
#     assert df_rivm_2020_07_24.equals(df_rivm_historical)
#
#
# def test_get_rivm_files_historical():
#     df_rivm_historical = get_rivm_files_historical(datetime.date(2020, 7, 24), datetime.date(2020, 7, 25))
#     available_dates = df_rivm_historical.index.unique()
#     assert len(available_dates) == 2
#     for dt in available_dates:
#         assert (dt.day == 24 or dt.day == 25) and dt.month == 7 and dt.year == 2020
#
#
def test_get_latest_rki_file():
    dataset = get_latest_rki_file()
    assertions_for_rki_df(dataset)

    # Populate local cache
    dir_path = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(dir_path, '../../..')
    dt = dataset.index.unique()[0].date()
    repository = LocalCacheRepository(folder)
    repository.write_dataset(dt, dataset)


def assertions_for_rki_df(df, dt: datetime.date = None):
    assert df.index.name == "Datenstand"
    assert "Refdatum" in df
    unique_dates = df.index.unique()
    assert len(unique_dates) == 1
    if dt is not None:
        assert unique_dates[0].date() == dt

# def test_get_cases_per_day_historical():
#     cases_per_day_list = get_cases_per_day_historical(datetime.date(2020, 7, 24), datetime.date(2020, 7, 25))
#     assert len(cases_per_day_list) == 2
#     assert cases_per_day_list[0][0] == datetime.date(2020, 7, 24)
#     assert isinstance(cases_per_day_list[0][1], Series)
#     assert cases_per_day_list[1][0] == datetime.date(2020, 7, 25)
#     assert isinstance(cases_per_day_list[1][1], Series)


def test_get_from_CharlesStr():
    df_rki = get_rki_file_historical_from_CharlesStr(datetime.date(2020, 6, 8))
    assertions_for_rki_df(df_rki, datetime.date(2020, 6, 8))


def test_get_from_CharlesStr_does_not_exist():
    df_rki = get_rki_file_historical_from_CharlesStr(datetime.date(2019, 3, 26))
    assert df_rki is None


def test_get_from_ihucos():
    df_rki = get_rki_file_historical_from_ihucos(datetime.date(2020, 6, 8))
    assertions_for_rki_df(df_rki, datetime.date(2020, 6, 8))


def test_get_from_ihucos_does_not_exist():
    df_rki = get_rki_file_historical_from_ihucos(datetime.date(2020, 12, 9))
    assert df_rki is None


def test_get_from_micb25():
    df_rki = get_rki_file_historical_from_micb25(datetime.date(2020, 6, 8))
    assertions_for_rki_df(df_rki, datetime.date(2020, 6, 8))


def test_get_from_micb25_does_not_exist():
    df_rki = get_rki_file_historical_from_micb25(datetime.date(2020, 3, 20))
    assert df_rki is None


def test_get_from_github():
    df_rki = get_rki_file_historical_from_github(datetime.date(2020, 12, 9))
    assertions_for_rki_df(df_rki, datetime.date(2020, 12, 9))


def test_get_from_github_does_not_exist():
    with pytest.raises(Exception) as excinfo:
        _ = get_rki_file_historical_from_github(datetime.date(2020, 3, 20))
    assert "Could not find historical RKI file" in str(excinfo.value)


def test_get_cases_per_day(df_rki_2020_07_24):
    # Slight difference with reported number of 204183 in:
    # https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Situationsberichte/2020-07-24-en.pdf?__blob=publicationFile
    # but could potentially be explained by timing of when data has been retrieved.
    ds_cases_per_day = get_cases_per_day_from_data_frame(df_rki_2020_07_24)
    assert sum(ds_cases_per_day) == 204170
