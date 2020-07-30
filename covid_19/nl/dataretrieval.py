import pandas as pd
from covid_19.pandasutils import filter_data_frame


def get_rivm_file(file_name):
    df_rivm = pd.read_csv(file_name)
    df_rivm["Date_file"] = pd.to_datetime(df_rivm["Date_file"], format='%Y-%m-%d')
    df_rivm["Date_statistics"] = pd.to_datetime(df_rivm["Date_statistics"], format='%Y-%m-%d')
    df_rivm.set_index("Date_file", inplace=True)
    return df_rivm


def get_latest_rivm_file():
    # An explanation of variables available in this dataset can be found at:
    # https://data.rivm.nl/geonetwork/srv/dut/catalog.search#/metadata/2c4357c8-76e4-4662-9574-1deb8a73f724?tab=relations
    # Currently the dataset is available daily at 14:15 NL time
    url = "https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.csv"
    df_rivm = pd.read_csv(url, sep=";")
    df_rivm["Date_file"] = pd.to_datetime(df_rivm["Date_file"], format='%Y-%m-%d')
    df_rivm["Date_statistics"] = pd.to_datetime(df_rivm["Date_statistics"], format='%Y-%m-%d')
    df_rivm.set_index("Date_file", inplace=True)
    return df_rivm


def get_cases_per_day_from_data_frame(df_rivm: pd.DataFrame, date_file=None) -> pd.Series:
    if date_file is None:
        date_file = df_rivm.index.unique()
        if len(date_file) > 1:
            raise Exception("Entered data frame contained more dates - please specify which date")
        date_file = date_file[0]

    df_filtered = filter_data_frame(df_rivm, date_file)
    return df_filtered["Date_statistics"].value_counts().sort_index()


def get_cases_per_day_from_file(folder):
    return pd.read_csv(folder + r"data\nl\COVID-19_daily_cases.csv", squeeze=True, index_col=0, header=None, parse_dates=True)


def get_lagged_values(folder):
    return pd.read_csv(folder + r"data\nl\COVID-19_lagged.csv", index_col=0, header=0, parse_dates=True)
