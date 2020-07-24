import pandas as pd


def get_latest_rivm_file():
    url = "https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.csv"
    return pd.read_csv(url)


def update_files(folder):
    df_daily_cases = pd.read_csv(folder + r"\COVID-19_daily_cases.csv")
    df_lagged = pd.read_csv(folder + r"\COVID-19_lagged.csv")

