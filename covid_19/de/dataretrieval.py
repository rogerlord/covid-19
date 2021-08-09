from urllib.error import HTTPError
import pandas as pd
from covid_19.dateutils import to_date
from covid_19.pandasutils import filter_data_frame
import datetime
import numpy as np
import requests
from zipfile import ZipFile
import tempfile
import os
import gzip


USED_COLS = ["AnzahlFall", "Meldedatum", "Datenstand", "NeuerFall", "Refdatum"]
REPORTING_LAG = 1


class RkiAndGitHubRepositoryWithCaching:
    def __init__(self, dt: datetime.date, folder: str):
        self.dt = dt
        self.rki_repository = RkiRepository(dt)
        self.github_repository = GitHubRepository()
        self.localcache_repository = LocalCacheRepository(folder)
        self.cache = dict()

    def get_dataset(self, dt: datetime.date):
        dt = to_date(dt)
        if dt in self.cache:
            return self.cache[dt]

        dataset = self.localcache_repository.get_dataset(dt)
        if dataset is not None:
            self.cache[dt] = dataset
            return dataset

        if dt == self.dt:
            dataset = self.rki_repository.get_dataset(dt)
            self.localcache_repository.write_dataset(dt, dataset)
            self.cache[dt] = dataset
            return dataset

        dataset = self.github_repository.get_dataset(dt)
        self.localcache_repository.write_dataset(dt, dataset)
        self.cache[dt] = dataset
        return dataset


class LocalCacheRepository:
    def __init__(self, folder: str):
        self.folder = os.path.join(folder, ".localcache/de")
        if not os.path.exists(self.folder):
            os.makedirs(self.folder, exist_ok=True)

    def get_full_filename(self, dt: datetime.date):
        file_name_start = "RKI_COVID19_"
        file_name = file_name_start + dt.strftime("%Y-%m-%d") + ".csv"
        return os.path.join(self.folder, file_name)

    def get_dataset(self, dt: datetime.date):
        full_file_name = self.get_full_filename(dt)
        if not os.path.isfile(full_file_name):
            return None

        dataset = get_latest_rki_file()
        return dataset

    def write_dataset(self, dt: datetime.date, df: pd.DataFrame):
        full_file_name = self.get_full_filename(dt)
        if not os.path.isfile(full_file_name):
            df.to_csv(full_file_name)


class RkiRepository:
    def __init__(self, dt: datetime.date):
        self.dt = dt

    def get_dataset(self, dt: datetime.date):
        if dt != self.dt:
            raise Exception("The RKI only stores the most recently available casus datasets.")

        df_rivm = get_latest_rki_file()
        if df_rivm.index.unique()[0].date() != self.dt:
            raise Exception("The RKI file available online does not correspond to the requested date " +
                            self.dt.strftime("%Y-%m-%d"))

        return df_rivm


class GitHubRepository:
    @staticmethod
    def get_dataset(dt: datetime.date):
        return get_rki_file_historical_from_github(dt)


def get_rki_file_historical_from_github(dt: datetime.date):
    df_rki = get_rki_file_historical_from_CharlesStr(dt)
    if df_rki is not None:
        return df_rki
    df_rki = get_rki_file_historical_from_micb25(dt)
    if df_rki is not None:
        return df_rki
    df_rki = get_rki_file_historical_from_ihucos(dt)
    if df_rki is not None:
        return df_rki
    raise Exception("Could not find historical RKI file for date: {date_str}".format(date_str=dt.strftime("%Y-%m-%d")))


def get_rki_file_historical_from_micb25(dt: datetime.date):
    url = "https://github.com/micb25/RKI_COVID19_DATA/raw/master/"
    url += "RKI_COVID19_" + dt.strftime("%Y-%m-%d") + ".csv.gz"

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_unpacked = tempfile.NamedTemporaryFile(delete=False)

    zip_request = requests.get(url)
    if zip_request.status_code != 200:
        return None

    try:
        temp_file.write(zip_request.content)
        temp_file.close()
        input_file = gzip.GzipFile(temp_file.name, "rb")
        try:
            temp_file_unpacked.write(input_file.read())
        finally:
            input_file.close()
            temp_file_unpacked.close()

        df_zip_file = get_rki_data_frame(temp_file_unpacked.name)
    finally:
        temp_file.close()
        os.remove(temp_file.name)
        os.remove(temp_file_unpacked.name)

    return df_zip_file


def get_rki_file_historical_from_ihucos(dt: datetime.date):
    url = "https://github.com/ihucos/rki-covid19-data/releases/download/"
    dt_plus_one = dt + datetime.timedelta(days=1)
    url += "/" + dt_plus_one.strftime("%Y-%m-%d") + "/data.csv"
    return get_rki_data_frame(url)


def get_rki_file_historical_from_CharlesStr(dt: datetime.date):
    url = "https://github.com/CharlesStr/CSV-Dateien-mit-Covid-19-Infektionen-/raw/master/"
    month_subfolder_lookup = {
        1: "Januar",
        2: "Februar",
        3: "Maerz",
        4: "April",
        5: "Mai",
        6: "Juni",
        7: "July",
        8: "August",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Dezember"}
    rki_file_name = "RKI_COVID19_{date_string}".format(date_string=dt.strftime("%Y-%m-%d"))
    if dt.year > 2020:
        url += month_subfolder_lookup[dt.month] + str(dt.year)
    else:
        url += month_subfolder_lookup[dt.month]
    url += "/" + rki_file_name

    if dt < datetime.date(2020, 9, 17):
        return get_rki_data_frame(url + ".csv")

    url += ".zip"
    zip_request = requests.get(url)
    if zip_request.status_code != 200:
        return None

    temp_file = tempfile.TemporaryFile()
    temp_dir = tempfile.TemporaryDirectory()

    try:
        temp_file.write(zip_request.content)
        temp_file.seek(os.SEEK_SET)

        with ZipFile(temp_file, 'r') as zip_file_reference:
            temp_zip_file = zip_file_reference.extract(rki_file_name + ".csv", path=temp_dir.name)

        df_zip_file = get_rki_data_frame(temp_zip_file)
    finally:
        temp_file.close()
        temp_dir.cleanup()

    return df_zip_file


def __is_int(s: str):
    try:
        int(s)
        return True
    except ValueError:
        return False


def __convert_date_column(ds):
    if __is_int(ds.iloc[0]):
        return ds.apply(lambda x: datetime.datetime.utcfromtimestamp(x / 1000))
    if "Uhr" in ds.iloc[0]:
        return pd.to_datetime(  ds, format="%d.%m.%Y, %H:%M Uhr", errors="ignore", utc=True)
    return pd.to_datetime(ds, format="%Y/%m/%d", utc=True)


def get_rki_data_frame(url):
    # An explanation of variables available in this dataset can be found at:
    # https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0
    # The dataset is available daily
    try:
        df_rki = pd.read_csv(url, sep=",", usecols=USED_COLS)
    except (HTTPError, FileNotFoundError):
        return None

    df_rki["Meldedatum"] = __convert_date_column(df_rki["Meldedatum"])
    df_rki["Refdatum"] = __convert_date_column(df_rki["Refdatum"])
    df_rki["Datenstand"] = __convert_date_column(df_rki["Datenstand"])
    df_rki.set_index("Datenstand", inplace=True)
    return df_rki


def get_latest_rki_file():
    # An explanation of variables available in this dataset can be found at:
    # https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0
    # The dataset is available daily
    url = "https://opendata.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0.csv"
    return get_rki_data_frame(url)


def get_cases_per_day_from_data_frame(df_rki: pd.DataFrame, date_file=None) -> pd.Series:
    if date_file is None:
        date_file = df_rki.index.unique()
        if len(date_file) > 1:
            raise Exception("Entered data frame contained more dates - please specify which date")
        date_file = date_file[0]

    df_filtered = filter_data_frame(df_rki, date_file)
    return df_filtered.groupby("Refdatum")["AnzahlFall"].agg("sum").sort_index()


class StatisticsRepository:
    def __init__(self, folder):
        self.folder = folder
        self.country_code = "de"

    def get_cases_per_day_from_file(self):
        return get_cases_per_day_from_file(self.folder)

    def get_lagged_values(self, maximum_lag=np.inf):
        return get_lagged_values(self.folder, maximum_lag)

    def get_measures(self):
        return get_measures(self.folder)

    @staticmethod
    def get_cases_per_day_from_data_frame(df_rivm: pd.DataFrame, date_file=None):
        return get_cases_per_day_from_data_frame(df_rivm, date_file)


def get_cases_per_day_from_file(folder):
    return pd.read_csv(folder + r"data\de\COVID-19_daily_cases.csv", squeeze=True, index_col=0, header=None, parse_dates=True)


def get_lagged_values(folder, maximum_lag=np.inf):
    df = pd.read_csv(folder + r"data\de\COVID-19_lagged.csv", index_col=0, header=0, parse_dates=True)
    if maximum_lag is np.inf:
        return df
    return df[df.columns[0:maximum_lag]]


def get_measures(folder):
    return pd.read_csv(folder + r"data\de\COVID-19_measures.csv", index_col=0, header=0, parse_dates=True)
