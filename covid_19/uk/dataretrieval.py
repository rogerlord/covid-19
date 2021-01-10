import pandas as pd
import datetime
import os

REPORTING_LAG = 1


class UkGovRepository:
    def __init__(self, dt: datetime.date, set_index: bool = True):
        self.dt = dt
        self.set_index = set_index

    def get_dataset(self, dt: datetime.date):
        if dt != self.dt:
            raise Exception("This repository only provides the most recently available casus datasets from coronavirus.data.gov.uk.")

        url = "https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=newCasesByPublishDate&metric=newCasesBySpecimenDate&format=csv"
        return get_uk_gov_dataframe_from_url(url, dt, self.set_index)


class UkGovHistoricalRepository:
    def __init__(self, set_index: bool = True):
        self.set_index = set_index

    def get_dataset(self, dt: datetime.date):
        url = "https://api.coronavirus.data.gov.uk/v2/data?areaType=overview&metric=newCasesByPublishDate&metric=newCasesBySpecimenDate&format=csv&release="
        url += dt.strftime("%Y-%m-%d")
        return get_uk_gov_dataframe_from_url(url, dt, self.set_index)


def get_uk_gov_dataframe_from_url(url: str, dt: datetime.date, set_index: bool = True):
    df_uk_gov = pd.read_csv(url, sep=",")
    df_uk_gov["date"] = pd.to_datetime(df_uk_gov["date"], format='%Y-%m-%d')
    if set_index:
        df_uk_gov["Date_file"] = dt.strftime("%Y-%m-%d")
        df_uk_gov.set_index("Date_file", inplace=True)
    return df_uk_gov


def is_uk_gov_historical_file_present(folder, dt: datetime.date):
    return os.path.exists(folder + r"\data\uk\historical\overview_{dt}.csv".format(dt=dt.strftime("%Y-%m-%d")))
