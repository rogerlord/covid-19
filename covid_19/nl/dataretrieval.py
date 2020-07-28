import pandas as pd


def get_latest_rivm_file():
    url = "https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.csv"
    df_rivm = pd.read_csv(url, sep=";")
    df_rivm["Date_file"] = pd.to_datetime(df_rivm["Date_file"], format='%Y-%m-%d')
    df_rivm["Date_statistics"] = pd.to_datetime(df_rivm["Date_statistics"], format='%Y-%m-%d')
    df_rivm.set_index("Date_file", inplace=True)
    return df_rivm


def get_daily_cases(folder):
    return pd.read_csv(folder + r"data\nl\COVID-19_daily_cases.csv", squeeze=True, index_col=0, header=None, parse_dates=True)


def get_lagged_values(folder):
    return pd.read_csv(folder + r"data\nl\COVID-19_lagged.csv", index_col=0, header=0, parse_dates=True)
