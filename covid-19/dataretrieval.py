import pandas as pd


def get_latest_rivm_file():
    url = "https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.csv"
    return pd.read_csv(url)