import pandas as pd
import datetime
from covid_19.nl.demography import get_ggd_regions
from covid_19.nl.dataretrieval import get_rivm_files_historical
from covid_19.nl.measures import calculate_measure_historically, net_increases, gross_increases
from covid_19.nl.updating import update_measures
import pytest


@pytest.mark.skip("Only run manually")
def test_create_data_frame_with_measures():
    df_rivm_historical = get_rivm_files_historical(datetime.date(2020, 7, 1), datetime.date(2020, 7, 30))
    print("Retrieved all data")
    date_range = pd.date_range(start=datetime.date(2020, 7, 2), end=datetime.date(2020, 7, 30))
    df_big = pd.DataFrame(index=date_range)

    net_increases_21 = lambda df1, df2: net_increases(df1, df2, 21)
    gross_increases_21 = lambda df1, df2: gross_increases(df1, df2, 21)

    ggd_regions = get_ggd_regions()
    for ggd_region in ggd_regions["Municipal_health_service"]:
        df_big["net_" + ggd_region] = calculate_measure_historically(df_rivm_historical, net_increases, ggd_region=ggd_region)
        df_big["gross_" + ggd_region] = calculate_measure_historically(df_rivm_historical, gross_increases, ggd_region=ggd_region)
        df_big["net_21_" + ggd_region] = calculate_measure_historically(df_rivm_historical, net_increases_21, ggd_region=ggd_region)
        df_big["gross_21_" + ggd_region] = calculate_measure_historically(df_rivm_historical, gross_increases_21, ggd_region=ggd_region)
        print("Calculated all data for {ggd_region}".format(ggd_region=ggd_region))

    df_big["net_nl"] = calculate_measure_historically(df_rivm_historical, net_increases)
    df_big["gross_nl"] = calculate_measure_historically(df_rivm_historical, gross_increases)
    df_big["net_21_nl"] = calculate_measure_historically(df_rivm_historical, net_increases_21)
    df_big["gross_nl"] = calculate_measure_historically(df_rivm_historical, gross_increases_21)

    df_big.to_csv(r"c:\temp\df_big_measures.csv")


@pytest.mark.skip("Only run manually")
def test_update_measures():
    df_measures = pd.read_csv(r"C:\Projects\covid-19\covid_19\tests\nl\fixtures\COVID-19_measures.csv"
                              , index_col=0, header=0, parse_dates=True)
    df_measures.index = pd.to_datetime(df_measures.index, format='%Y-%m-%d')
    df_measures_updated = update_measures(df_measures)
    df_measures_updated.to_csv(r"c:\temp\df_measures.csv", date_format="%Y-%m-%d")
