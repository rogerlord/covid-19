from covid_19.se.dataretrieval import get_daily_cases_historical
import datetime
import pandas as pd
import pytest


@pytest.mark.skip("Work in progress")
def test_get_daily_cases_historical():
    start_date = datetime.date(2020, 7, 1)
    df_list = []

    for i in range(38):
        dt = start_date + datetime.timedelta(days=i)
        try:
            df = get_daily_cases_historical(dt)
            df = df.reset_index()
            df["Date_file"] = dt
            df = df.set_index("Date_file")
            df_list.append(df)
        except:
            continue
    df_big = pd.concat(df_list)
    df_big.to_csv(r"c:\temp\df_sweden.csv")
