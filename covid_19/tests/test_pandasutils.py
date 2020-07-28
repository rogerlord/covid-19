import pandas as pd
import datetime
from pandasutils import filter_data_frame, filter_series
import pytest


@pytest.mark.parametrize("hour", [0, 10])
def test_filter_data_frame(hour):
    date_range = pd.date_range(start=datetime.datetime(2020, 7, 2, hour), end=datetime.datetime(2020, 7, 26, hour),
                               freq="D")
    col1 = [dt.day for dt in date_range]
    col2 = [dt.day + 1 for dt in date_range]
    df = pd.DataFrame(index=date_range, data={"col1": col1, "col2": col2})
    df_filtered = filter_data_frame(df, datetime.date(2020, 7, 3))
    assert len(df_filtered) == 1
    dt = df_filtered.index[0]
    assert dt.day == 3 and dt.month == 7 and dt.year == 2020


@pytest.mark.parametrize("hour", [0, 10])
def test_filter_series(hour):
    date_range = pd.date_range(start=datetime.datetime(2020, 7, 2, hour), end=datetime.datetime(2020, 7, 26, hour),
                               freq="D")
    ds = pd.Series(index=date_range, data=date_range)
    series_filtered = filter_series(ds, datetime.date(2020, 7, 3), datetime.date(2020, 7, 4))
    assert len(series_filtered) == 2
    for dt in series_filtered.index:
        assert dt.month == 7 and dt.year == 2020
        assert dt.day == 3 or dt.day == 4
