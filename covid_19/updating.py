import datetime
import pandas as pd
from covid_19.pandasutils import filter_series


def update_lagged_values(df_lagged, ds_daily_cases, dt, reporting_lag=0):
    df = df_lagged.copy()

    dt_corrected_for_reporting_lag = dt - datetime.timedelta(days=reporting_lag)
    last_contribution = filter_series(ds_daily_cases, dt_corrected_for_reporting_lag, dt_corrected_for_reporting_lag)
    if len(last_contribution) == 0:
        print("Zero patients reported on {dt}".format(dt=dt_corrected_for_reporting_lag))
        last_contribution = 0
    elif len(last_contribution) > 1:
        raise Exception("More than one contribution on {dt}".format(dt=dt_corrected_for_reporting_lag))
    else:
        last_contribution = last_contribution.iloc[0]

    new_last_row = pd.Series(data=[last_contribution],
                             index=['0'],
                             name=datetime.datetime.combine(dt_corrected_for_reporting_lag, datetime.datetime.min.time()))

    df = df.append(new_last_row)
    for i in range(1, len(df_lagged.columns)):
        infection_date = dt_corrected_for_reporting_lag - datetime.timedelta(days=i)
        value_to_add = ds_daily_cases[infection_date]
        infection_date_datetime = datetime.datetime.combine(infection_date, datetime.datetime.min.time())
        df.at[infection_date_datetime, str(i)] = value_to_add

    return df
