import pandas as pd
from covid_19.pandasutils import filter_data_frame
from covid_19.manipulation import create_lagged_values_differences
import datetime
import numpy as np


class RivmRepository:
    def __init__(self, dt: datetime.date):
        self.dt = dt

    def get_dataset(self, dt: datetime.date):
        if dt != self.dt:
            raise Exception("The RIVM only stores the most recently available casus datasets.")

        df_rivm = get_latest_rivm_file()
        if df_rivm.index.unique()[0].date() != self.dt:
            raise Exception("The RIVM file available online does not correspond to the requested date " +
                            self.dt.strftime("%Y-%m-%d"))

        return df_rivm


class GithubRepository:
    @staticmethod
    def get_dataset(dt: datetime.date):
        return get_rivm_file_historical(dt)


def get_rivm_file_historical(date_file):
    # Marino van Zelst (mzelst) kindly stores the history of the RIVM files in his GitHub repository
    uri = "https://raw.githubusercontent.com/mzelst/covid-19/master/data-rivm/casus-datasets/"
    file_name_start = "COVID-19_casus_landelijk_"
    return get_rivm_file(uri + file_name_start + date_file.strftime("%Y-%m-%d") + ".csv")


def get_rivm_files_historical(from_date, to_date):
    df_list = []
    for i in range((to_date - from_date).days + 1):
        dt = from_date + datetime.timedelta(days=i)
        df_list.append(get_rivm_file_historical(dt))

    return pd.concat(df_list, axis=0, sort=True)


def get_rivm_file(file_name):
    df_rivm = pd.read_csv(file_name, usecols=["Date_file", "Date_statistics", "Agegroup", "Municipal_health_service"])
    df_rivm["Date_file"] = pd.to_datetime(df_rivm["Date_file"], format='%Y-%m-%d')
    df_rivm["Date_statistics"] = pd.to_datetime(df_rivm["Date_statistics"], format='%Y-%m-%d')
    df_rivm.set_index("Date_file", inplace=True)
    return df_rivm


def get_latest_rivm_file():
    # An explanation of variables available in this dataset can be found at:
    # https://data.rivm.nl/geonetwork/srv/dut/catalog.search#/metadata/2c4357c8-76e4-4662-9574-1deb8a73f724?tab=relations
    # Currently the dataset is available daily at 14:15 NL time
    url = "https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.csv"
    df_rivm = pd.read_csv(url, sep=";", usecols=["Date_file", "Date_statistics", "Agegroup", "Municipal_health_service"])
    df_rivm["Date_file"] = pd.to_datetime(df_rivm["Date_file"], format='%Y-%m-%d')
    df_rivm["Date_statistics"] = pd.to_datetime(df_rivm["Date_statistics"], format='%Y-%m-%d')
    df_rivm.set_index("Date_file", inplace=True)
    return df_rivm


def get_cases_per_day_from_data_frame(df_rivm: pd.DataFrame, date_file=None, ggd_region=None) -> pd.Series:
    if date_file is None:
        date_file = df_rivm.index.unique()
        if len(date_file) > 1:
            raise Exception("Entered data frame contained more dates - please specify which date")
        date_file = date_file[0]

    df_filtered = filter_data_frame(df_rivm, date_file)
    if ggd_region is not None:
        df_filtered = df_filtered[df_filtered["Municipal_health_service"] == ggd_region]

    return df_filtered["Date_statistics"].value_counts().sort_index()


def get_cases_per_day_from_file(folder):
    return pd.read_csv(folder + r"data\nl\COVID-19_daily_cases.csv", squeeze=True, index_col=0, header=None, parse_dates=True)


def get_cases_per_day_historical(from_date, to_date):
    cases_per_day_list = []

    for i in range((to_date - from_date).days + 1):
        dt = from_date + datetime.timedelta(days=i)
        df = get_cases_per_day_from_data_frame(get_rivm_file_historical(dt))
        cases_per_day_list.append((dt, df))

    return cases_per_day_list


def get_lagged_values(folder, maximum_lag=np.inf):
    df = pd.read_csv(folder + r"data\nl\COVID-19_lagged.csv", index_col=0, header=0, parse_dates=True)
    if maximum_lag is np.inf:
        return df
    return df[df.columns[0:maximum_lag]]


def get_daily_reported_values(folder):
    df_lagged = get_lagged_values(folder)
    return create_lagged_values_differences(df_lagged.to_numpy())


def get_measures(folder):
    return pd.read_csv(folder + r"data\nl\COVID-19_measures.csv", index_col=0, header=0, parse_dates=True)
