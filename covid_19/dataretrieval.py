import pandas as pd
import datetime


def get_latest_rivm_file():
    url = "https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.csv"
    df_rivm = pd.read_csv(url, sep=";")
    df_rivm["Date_file"] = pd.to_datetime(df_rivm["Date_file"], format='%Y-%m-%d')
    df_rivm["Date_statistics"] = pd.to_datetime(df_rivm["Date_statistics"], format='%Y-%m-%d')
    df_rivm.set_index("Date_file", inplace=True)
    return df_rivm


def get_daily_cases(folder):
    return pd.read_csv(folder + r"data\COVID-19_daily_cases.csv", squeeze=True, index_col=0, header=None, parse_dates=True)


def get_lagged_values(folder):
    return pd.read_csv(folder + r"data\COVID-19_lagged.csv", index_col=0, header=0, parse_dates=True)


def get_values_on_date(data_frame, requested_date):
    requested_date_datetime = datetime.datetime.combine(requested_date, datetime.datetime.min.time())
    requested_date_datetime_next_day = requested_date_datetime + datetime.timedelta(days=1)
    return data_frame[requested_date_datetime:requested_date_datetime_next_day]


def update_files(folder):
    df_daily_cases = get_daily_cases(folder)
    df_rivm = get_latest_rivm_file()
    last_available_date = max(df_daily_cases.index).date()
    last_available_date_rivm = max(df_rivm.index).date()
    if not last_available_date_rivm > last_available_date:
        return

    df_daily_cases_updated = get_values_on_date(df_rivm, last_available_date_rivm)["Date_statistics"].value_counts()
    df_daily_cases_updated.sort_index(inplace=True)
    df_daily_cases_updated.to_csv(folder + r"data\COVID-19_daily_cases.csv", header=False)

    df_lagged = get_lagged_values(folder)
    new_last_row = pd.Series(data=[df_daily_cases_updated[last_available_date_rivm]],
                             index=['0'],
                             name=datetime.datetime.combine(last_available_date_rivm, datetime.datetime.min.time()))
    df_lagged = df_lagged.append(new_last_row)
    for i in range(1, len(df_lagged.columns)):
        infection_date = last_available_date_rivm - datetime.timedelta(days=i)
        print(infection_date)
        value_to_add = df_daily_cases_updated[infection_date]
        df_lagged.at[infection_date, str(i)] = value_to_add
    df_lagged.to_csv(folder + r"data\COVID-19_lagged.csv", header=True)
