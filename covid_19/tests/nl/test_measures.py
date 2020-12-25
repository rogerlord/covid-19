import pytest
import os
from covid_19.nl.forecasting import forecast_daily_cases


@pytest.mark.skip("Only run locally")
def test_generate_nowcasts():
    current_path = os.path.dirname(os.path.realpath(__file__))
    folder = os.path.join(current_path, r"../../../")
    df_updated = forecast_daily_cases(folder, beta=0.2, maximum_lag=14)
    data_forecast = df_updated.dropna()
    data_rolling = data_forecast.rolling(window=7).mean().dropna()
    data_rolling.to_csv("c:\\temp\\nowcasts.csv")
