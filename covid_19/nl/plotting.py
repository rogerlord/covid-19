from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.io import export_png
from bokeh.models import DatetimeTickFormatter
from bokeh.palettes import Spectral10
from covid_19.nl.dataretrieval import get_daily_cases
from covid_19.nl.forecasting import forecast_daily_cases


def generate_plot(folder, show_only_last):
    df_daily = get_daily_cases(folder)
    df_updated = forecast_daily_cases(folder)
    data_actual = df_daily.dropna()[-show_only_last:]
    data_forecast = df_updated.dropna()[-show_only_last:]
    data_rolling = df_updated.rolling(window=7).mean().dropna()[-show_only_last:]

    data_dict = {"Date": data_actual.index, "Value": data_actual.array }
    data_forecast_dict = {"Date": data_forecast.index, "Value": data_forecast.array}
    data_rolling_dict = {"Date": data_rolling.index, "Value": data_rolling.array}

    source = ColumnDataSource(data_dict)
    source_forecast = ColumnDataSource(data_forecast_dict)
    source_rolling = ColumnDataSource(data_rolling_dict)

    p = figure(x_axis_type="datetime", plot_width=800, plot_height=350)
    p.line('Date', 'Value', source=source, line_width=1, legend_label="Current data", line_color=Spectral10[1])
    p.line('Date', 'Value', source=source_forecast, line_dash="dashed", line_width=1, legend_label="Forecast", line_color=Spectral10[9])
    p.line('Date', 'Value', source=source_rolling, line_width=5, legend_label="7-day rolling average", line_color=Spectral10[0])
    p.xaxis.formatter = DatetimeTickFormatter(days="%d/%b", months="%d/%b", hours="%d/%b", minutes="%d/%b")
    p.yaxis.axis_label = "Daily new COVID-19 infections"
    p.legend.location = "top_left"

    export_png(p, filename=folder + r"plots\nl\COVID-19_daily_cases_plot.png")
