import pandas as pd
import datetime
import os
import numpy as np
from covid_19.pandasutils import filter_data_frame

REPORTING_LAG = 1
PUBLICATION_LAG = 1


class FileRepository:
    def __init__(self, folder):
        self.folder = folder

    def get_dataset(self, dt: datetime.date):
        return get_uk_gov_dataframe_from_file(self.folder, dt - datetime.timedelta(days=PUBLICATION_LAG))


class UkGovRepository:
    def __init__(self, dt: datetime.date, set_index: bool = True):
        self.dt = dt
        self.set_index = set_index

    def get_dataset(self, dt: datetime.date):
        if dt != self.dt:
            raise Exception("This repository only provides the most recently available casus datasets from coronavirus.data.gov.uk.")

        url = "https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=newCasesByPublishDate&metric=newCasesBySpecimenDate&format=csv"
        return get_uk_gov_dataframe_from_url(url, dt - datetime.timedelta(days=PUBLICATION_LAG), self.set_index)


class UkGovHistoricalRepository:
    def __init__(self, set_index: bool = True):
        self.set_index = set_index

    def get_dataset(self, dt: datetime.date):
        retrieval_date = dt - datetime.timedelta(days=PUBLICATION_LAG)
        url = "https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=newCasesByPublishDate&metric=newCasesBySpecimenDate&format=csv&release="
        url += retrieval_date.strftime("%Y-%m-%d")
        return get_uk_gov_dataframe_from_url(url, retrieval_date, self.set_index)


def get_uk_gov_dataframe_from_file(folder, dt: datetime.date):
    return get_uk_gov_dataframe_from_url(folder + r"/data/uk/historical/overview_{dt}.csv".format(dt=dt.strftime("%Y-%m-%d")), dt)


def get_uk_gov_dataframe_from_url(url: str, dt: datetime.date, set_index: bool = True):
    df_uk_gov = pd.read_csv(url, sep=",")
    df_uk_gov["date"] = pd.to_datetime(df_uk_gov["date"], format='%Y-%m-%d')
    if set_index:
        df_uk_gov["Date_file"] = pd.to_datetime(dt)
        df_uk_gov.set_index("Date_file", inplace=True)

    return df_uk_gov


def is_uk_gov_historical_file_present(folder, dt: datetime.date):
    return os.path.exists(folder + r"\data\uk\historical\overview_{dt}.csv".format(dt=dt.strftime("%Y-%m-%d")))


def get_cases_per_day_from_file(folder):
    return pd.read_csv(folder + r"data\uk\COVID-19_daily_cases.csv", squeeze=True, index_col=0, header=None, parse_dates=True)


def get_lagged_values(folder, maximum_lag=np.inf):
    df = pd.read_csv(folder + r"data\uk\COVID-19_lagged.csv", index_col=0, header=0, parse_dates=True)
    if maximum_lag is np.inf:
        return df
    return df[df.columns[0:maximum_lag]]


def get_cases_per_day_from_data_frame(df_uk_gov: pd.DataFrame, date_file=None) -> pd.Series:
    if date_file is None:
        date_file = df_uk_gov.index.unique()
        if len(date_file) > 1:
            raise Exception("Entered data frame contained more dates - please specify which date")
        date_file = date_file[0]

    df_filtered = filter_data_frame(df_uk_gov, date_file)
    return df_filtered.groupby("date")["newCasesBySpecimenDate"].agg("sum").sort_index()
