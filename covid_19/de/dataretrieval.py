import pandas as pd
from covid_19.pandasutils import filter_data_frame
from manipulation import create_lagged_values_differences
import datetime
import numpy as np


# class RivmRepository:
#     def __init__(self, dt: datetime.date):
#         self.dt = dt
#
#     def get_dataset(self, dt: datetime.date):
#         if dt != self.dt:
#             raise Exception("The RIVM only stores the most recently available casus datasets.")
#
#         df_rivm = get_latest_rivm_file()
#         if df_rivm.index.unique()[0].date() != self.dt:
#             raise Exception("The RIVM file available online does not correspond to the requested date " +
#                             self.dt.strftime("%Y-%m-%d"))
#
#         return df_rivm
#
#
# class GithubRepository:
#     @staticmethod
#     def get_dataset(dt: datetime.date):
#         return get_rivm_file_historical(dt)
#
#
# def get_rivm_file_historical(date_file):
#     # The first does not have a consistent history, the second does - maybe use a combination?
#     # https://github.com/ihucos/rki-covid19-data/releases
#     # https://github.com/CharlesStr/CSV-Dateien-mit-Covid-19-Infektionen-
#     # Marino van Zelst (mzelst) kindly stores the history of the RIVM files in his GitHub repository
#     uri = "https://raw.githubusercontent.com/mzelst/covid-19/master/data-rivm/casus-datasets/"
#     file_name_start = "COVID-19_casus_landelijk_"
#     return get_rivm_file(uri + file_name_start + date_file.strftime("%Y-%m-%d") + ".csv")
#
#
# def get_rivm_files_historical(from_date, to_date):
#     df_list = []
#     for i in range((to_date - from_date).days + 1):
#         dt = from_date + datetime.timedelta(days=i)
#         df_list.append(get_rivm_file_historical(dt))
#
#     return pd.concat(df_list, axis=0, sort=True)
#
#
# def get_rivm_file(file_name):
#     df_rivm = pd.read_csv(file_name)
#     df_rivm["Date_file"] = pd.to_datetime(df_rivm["Date_file"], format='%Y-%m-%d')
#     df_rivm["Date_statistics"] = pd.to_datetime(df_rivm["Date_statistics"], format='%Y-%m-%d')
#     df_rivm.set_index("Date_file", inplace=True)
#     return df_rivm


def get_latest_rki_file():
    # An explanation of variables available in this dataset can be found at:
    # https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0
    # The dataset is available daily
    url = "https://opendata.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0.csv"
    df_rki = pd.read_csv(url, sep=",", usecols=["AnzahlFall", "Meldedatum", "Datenstand",
                                                "NeuerFall", "Refdatum"])
    df_rki["Meldedatum"] = pd.to_datetime(df_rki["Meldedatum"], format='%Y/%m/%d')
    df_rki["Refdatum"] = pd.to_datetime(df_rki["Refdatum"], format='%Y/%m/%d')
    df_rki["Datenstand"] = pd.to_datetime(df_rki["Datenstand"], format="%d.%m.%Y, %H:%M Uhr", errors="ignore")
    df_rki.set_index("Datenstand", inplace=True)
    return df_rki


# def get_cases_per_day_from_data_frame(df_rivm: pd.DataFrame, date_file=None, ggd_region=None) -> pd.Series:
#     if date_file is None:
#         date_file = df_rivm.index.unique()
#         if len(date_file) > 1:
#             raise Exception("Entered data frame contained more dates - please specify which date")
#         date_file = date_file[0]
#
#     df_filtered = filter_data_frame(df_rivm, date_file)
#     if ggd_region is not None:
#         df_filtered = df_filtered[df_filtered["Municipal_health_service"] == ggd_region]
#
#     return df_filtered["Date_statistics"].value_counts().sort_index()
#
#
# def get_cases_per_day_from_file(folder):
#     return pd.read_csv(folder + r"data\nl\COVID-19_daily_cases.csv", squeeze=True, index_col=0, header=None, parse_dates=True)
#
#
# def get_cases_per_day_historical(from_date, to_date):
#     cases_per_day_list = []
#
#     for i in range((to_date - from_date).days + 1):
#         dt = from_date + datetime.timedelta(days=i)
#         df = get_cases_per_day_from_data_frame(get_rivm_file_historical(dt))
#         cases_per_day_list.append((dt, df))
#
#     return cases_per_day_list
#
#
# def get_lagged_values(folder, maximum_lag=np.inf):
#     df = pd.read_csv(folder + r"data\nl\COVID-19_lagged.csv", index_col=0, header=0, parse_dates=True)
#     if maximum_lag is np.inf:
#         return df
#     return df[df.columns[0:maximum_lag]]
#
#
# def get_daily_reported_values(folder):
#     df_lagged = get_lagged_values(folder)
#     return create_lagged_values_differences(df_lagged.to_numpy())
#
#
# def get_measures(folder):
#     return pd.read_csv(folder + r"data\nl\COVID-19_measures.csv", index_col=0, header=0, parse_dates=True)
