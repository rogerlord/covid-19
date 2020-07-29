import pandas as pd
from dataretrieval import get_daily_cases, get_latest_rivm_file, get_lagged_values
import datetime
from covid_19.pandasutils import filter_data_frame, filter_series


def update_files(folder):
    df_daily_cases = get_daily_cases(folder)
    df_rivm = get_latest_rivm_file()
    last_available_date = max(df_daily_cases.index).date()
    last_available_date_rivm = max(df_rivm.index).date()
    if not last_available_date_rivm > last_available_date:
        return

    df_daily_cases_updated = filter_data_frame(df_rivm, last_available_date_rivm)["Date_statistics"].value_counts()
    df_daily_cases_updated.sort_index(inplace=True)
    df_daily_cases_updated.to_csv(folder + r"data\nl\COVID-19_daily_cases.csv", header=False)

    df_lagged = get_lagged_values(folder)
    last_contribution = filter_series(df_daily_cases_updated, last_available_date_rivm, last_available_date_rivm)
    if len(last_contribution) == 0:
        print("Zero patients reported on {dt}".format(dt=last_available_date_rivm))
        last_contribution = 0
    elif len(last_contribution) > 1:
        raise Exception("More than one contribution on {dt}".format(dt=last_available_date_rivm))
    else:
        last_contribution = last_contribution.iloc[0]

    new_last_row = pd.Series(data=[last_contribution],
                             index=['0'],
                             name=datetime.datetime.combine(last_available_date_rivm, datetime.datetime.min.time()))
    df_lagged = df_lagged.append(new_last_row)
    print(df_daily_cases_updated.index)
    for i in range(1, len(df_lagged.columns)):
        infection_date = last_available_date_rivm - datetime.timedelta(days=i)
        value_to_add = df_daily_cases_updated[infection_date]
        df_lagged.at[infection_date, str(i)] = value_to_add
    df_lagged.to_csv(folder + r"data\nl\COVID-19_lagged.csv", header=True)
