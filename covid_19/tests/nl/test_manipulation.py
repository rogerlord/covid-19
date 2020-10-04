from covid_19.nl.dataretrieval import get_cases_per_day_historical, get_cases_per_day_from_data_frame, \
    get_rivm_file_historical, get_lagged_values, get_daily_reported_values
from covid_19.nl.manipulation import create_lagged_values_data_frame, create_lagged_values_differences, \
    create_lagged_values_array, recreate_lagged_values
import pandas as pd
import datetime
import pytest
import os
from covid_19.tests.test_pandasutils import assert_frame_equal


@pytest.mark.skip("Only run locally")
def test_generate_lagged_values():
    start_date = datetime.date(2020, 7, 1)
    end_date = datetime.date(2020, 10, 4)

    cases_per_day_list = get_cases_per_day_historical(start_date, end_date)
    lagged_values_df = create_lagged_values_data_frame(cases_per_day_list, maximum_lag=31)

    lagged_values_df.to_csv(r"c:\temp\df_lagged.csv")


@pytest.mark.skip("Only run locally")
def test_generate_differences():
    start_date = datetime.date(2020, 7, 1)
    end_date = datetime.date(2020, 10, 3)

    df_list = []
    date_list = []
    for i in range((end_date - start_date).days + 1):
        dt = start_date + datetime.timedelta(days=i)
        df_list.append(get_cases_per_day_from_data_frame(get_rivm_file_historical(dt)))
        date_list.append(dt)

    num_lags = (end_date - start_date).days + 1
    bla = create_lagged_values_array(df_list, date_list)
    df = pd.DataFrame(bla, index=pd.date_range(start=start_date.strftime("%Y-%m-%d"),
                                               end=end_date.strftime("%Y-%m-%d")),
                      columns=range(num_lags))
    df.to_csv(r"c:\temp\df_lagged.csv")

    blabla = create_lagged_values_differences(bla)
    df_differences = pd.DataFrame(blabla, index=pd.date_range(start=start_date.strftime("%Y-%m-%d"),
                                                              end=end_date.strftime("%Y-%m-%d")),
                                  columns=range(num_lags))
    df_differences.to_csv(r"c:\temp\df_differences.csv")


@pytest.fixture
def covid_19_lagged_values():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, 'fixtures/COVID-19_lagged.csv')
    return pd.read_csv(file_name, index_col=0, header=0, parse_dates=True)


def test_recreate_lagged_values(covid_19_lagged_values):
    current_path = os.path.dirname(os.path.realpath(__file__))
    df_lagged_most_recent = get_lagged_values(os.path.join(current_path, r"../../../"), maximum_lag=14)
    df_lagged_recreated = recreate_lagged_values(df_lagged_most_recent, datetime.date(2020, 8, 8))
    assert_frame_equal(df_lagged_recreated, covid_19_lagged_values)


@pytest.mark.skip("Work in progress")
def test_work_in_progress():
    current_path = os.path.dirname(os.path.realpath(__file__))
    daily_reported_values = get_daily_reported_values(os.path.join(current_path, r"../../../"))
