import pandas as pd
import datetime
from covid_19.nl.demography import get_ggd_regions
from covid_19.nl.dataretrieval import get_rivm_files_historical, \
    get_cases_per_day_from_data_frame, get_rivm_file
from covid_19.nl.measures import calculate_measure_historically, net_increases, gross_increases
from covid_19.nl.updating import update_measures, update_lagged_values
from covid_19.tests.test_pandasutils import assert_frame_equal
import os
import pytest


@pytest.mark.skip("Only run manually")
def test_create_data_frame_with_measures():
    df_rivm_historical = get_rivm_files_historical(datetime.date(2020, 7, 1), datetime.date(2020, 7, 30))
    print("Retrieved all data")
    date_range = pd.date_range(start=datetime.date(2020, 7, 2), end=datetime.date(2020, 7, 30))
    df_big = pd.DataFrame(index=date_range)

    ggd_regions = get_ggd_regions()
    for ggd_region in ggd_regions["Municipal_health_service"]:
        df_big["net_" + ggd_region] = calculate_measure_historically(df_rivm_historical, net_increases,
                                                                     ggd_region=ggd_region)
        df_big["gross_" + ggd_region] = calculate_measure_historically(df_rivm_historical, gross_increases,
                                                                       ggd_region=ggd_region)
        print("Calculated all data for {ggd_region}".format(ggd_region=ggd_region))

    df_big["net_nl"] = calculate_measure_historically(df_rivm_historical, net_increases)
    df_big["gross_nl"] = calculate_measure_historically(df_rivm_historical, gross_increases)

    df_big.to_csv(r"c:\temp\df_big_measures.csv")


@pytest.mark.skip("Only run manually")
def test_update_measures():
    current_path = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(current_path, r"../../../")

    df_measures = pd.read_csv(r"C:\Projects\covid-19\covid_19\tests\nl\fixtures\COVID-19_measures.csv"
                              , index_col=0, header=0, parse_dates=True)
    df_measures.index = pd.to_datetime(df_measures.index, format='%Y-%m-%d')
    df_measures_updated = update_measures(df_measures, folder)
    df_measures_updated.to_csv(r"c:\temp\df_measures.csv", date_format="%Y-%m-%d")


def test_update_lagged_values():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name_lagged = os.path.join(dir_path, 'fixtures/COVID-19_lagged.csv')
    df_lagged = pd.read_csv(file_name_lagged, index_col=0, header=0, parse_dates=True)

    file_name_df_aug_9 = os.path.join(dir_path, 'fixtures/COVID-19_casus_landelijk_2020-08-09.csv')
    ds_daily_cases = get_cases_per_day_from_data_frame(get_rivm_file(file_name_df_aug_9))

    df_lagged_updated = update_lagged_values(df_lagged, ds_daily_cases, datetime.date(2020, 8, 9))

    file_name_lagged_updated_expected = os.path.join(dir_path, 'fixtures/COVID-19_lagged_updated.csv')
    df_lagged_updated_expected = pd.read_csv(file_name_lagged_updated_expected, index_col=0, header=0, parse_dates=True)

    assert_frame_equal(df_lagged_updated, df_lagged_updated_expected)
