import pandas as pd
from bokeh.io import export_png
from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.palettes import Spectral10
from bokeh.plotting import figure
import covid_19.chainladder as chainladder


def generate_plot_national_cases_per_day_chainladder(repository, statistics_repository, show_only_last, reporting_lag=0):
    df_daily = statistics_repository.get_cases_per_day_from_file()
    dt = df_daily.index.unique().max()

    corrected_cases_per_day = chainladder.nowcast_cases_per_day(dt, statistics_repository.get_lagged_values,
                                                                statistics_repository.get_cases_per_day_from_data_frame,
                                                                repository, beta=0.2, reporting_lag=reporting_lag)[0]
    df_updated = pd.Series(data=corrected_cases_per_day, index=df_daily.index[-len(corrected_cases_per_day):])

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
    p.title.text = "Positive tests - actual vs. nowcast"
    p.title.align = "center"
    p.title.text_font_size = "18px"
    p.line('Date', 'Value', source=source, line_dash="dashed", line_width=3, legend_label="Actual (not fully known)", line_color="black")
    p.line('Date', 'Value', source=source_forecast, line_dash="dashed", line_width=3, legend_label="Nowcast", line_color=Spectral10[2])
    p.line('Date', 'Value', source=source_rolling, line_width=4, legend_label="Nowcast (7-day rolling average)", line_color=Spectral10[0])
    p.xaxis.formatter = DatetimeTickFormatter(days="%d/%b", months="%d/%b", hours="%d/%b", minutes="%d/%b")
    p.yaxis.axis_label = "Positive tests"
    p.legend.location = "top_left"

    export_png(p, filename=statistics_repository.folder + r"plots\{country}\COVID-19_daily_cases_plot.png".format(country=statistics_repository.country_code))


def generate_plots_chainladder(repository, statistics_repository, start_date, skip_last, reporting_lag=0):
    df_daily = statistics_repository.get_cases_per_day_from_file()
    dt = df_daily.index.unique().max()

    nowcast_cases_per_day = chainladder.nowcast_cases_per_day(dt, statistics_repository.get_lagged_values,
                                                              statistics_repository.get_cases_per_day_from_data_frame,
                                                              repository, beta=0.2, reporting_lag=reporting_lag)[0]
    df_updated = pd.Series(data=nowcast_cases_per_day, index=df_daily.index[-len(nowcast_cases_per_day):])
    df_measures = statistics_repository.get_measures()
    nowcast_same_day_chain_0_2 = df_measures["nowcast_nl_chain_0_2"]
    nowcast_same_day_chain = df_measures["nowcast_nl_chain"]
    gross = df_measures["gross_nl"]

    data_actual = df_daily.dropna().rolling(window=7).mean().dropna()[start_date:]
    data_nowcast_chain_0_2 = df_updated.rolling(window=7).mean().dropna()[start_date:]
    data_nowcast_chain_0_2_same_day = nowcast_same_day_chain_0_2.dropna()[start_date:]
    data_nowcast_chain_same_day = nowcast_same_day_chain.dropna()[start_date:]
    data_gross = gross.rolling(window=7).mean().dropna()[start_date:]

    data_actual_dict = {"Date": data_actual.index, "Value": data_actual.array}
    data_nowcast_dict = {"Date": data_nowcast_chain_0_2.index, "Value": data_nowcast_chain_0_2.array}
    data_nowcast_same_day_dict = {"Date": data_nowcast_chain_0_2_same_day.index, "Value": data_nowcast_chain_0_2_same_day.array}
    data_gross_dict = {"Date": data_gross.index, "Value": data_gross.array}

    source_actual = ColumnDataSource(data_actual_dict)
    source_nowcast = ColumnDataSource(data_nowcast_dict)
    source_nowcast_same_day = ColumnDataSource(data_nowcast_same_day_dict)
    source_gross = ColumnDataSource(data_gross_dict)

    p = figure(x_axis_type="datetime", plot_width=800, plot_height=350)
    p.title.text = "7-day rolling average of positive tests"
    p.title.align = "center"
    p.title.text_font_size = "18px"
    p.line('Date', 'Value', source=source_actual, line_dash="dashed", line_width=4, legend_label="Actual (not fully known)", line_color='black')
    p.line('Date', 'Value', source=source_nowcast, line_width=4, legend_label="Nowcast", line_color=Spectral10[0])
    p.line('Date', 'Value', source=source_nowcast_same_day, line_dash="solid", line_dash_offset=2, line_width=4, legend_label="Nowcast (same-day)", line_color=Spectral10[2])
    p.line('Date', 'Value', source=source_gross, line_width=4, legend_label="Gross", line_color=Spectral10[1])
    p.xaxis.formatter = DatetimeTickFormatter(days="%d/%b", months="%d/%b", hours="%d/%b", minutes="%d/%b")
    p.yaxis.axis_label = "Positive tests"
    p.legend.location = "top_left"

    export_png(p, filename=statistics_repository.folder + r"plots\{country}\COVID-19_daily_cases_nowcast_performance.png".format(country=statistics_repository.country_code))

    # Calculate differences
    number_of_elements = len(data_actual) - skip_last
    data_gross_diff = (data_gross - data_actual)[:number_of_elements]
    data_nowcast_chain_0_2_diff = (data_nowcast_chain_0_2_same_day - data_actual)[:number_of_elements]
    data_nowcast_chain_diff = (data_nowcast_chain_same_day - data_actual)[:number_of_elements]

    source_gross_diff = ColumnDataSource({"Date": data_gross_diff.index, "Value": data_gross_diff.array})
    source_nowcast_chain_0_2_diff = ColumnDataSource({"Date": data_nowcast_chain_0_2_diff.index, "Value": data_nowcast_chain_0_2_diff.array})
    source_nowcast_chain_diff = ColumnDataSource({"Date": data_nowcast_chain_diff.index, "Value": data_nowcast_chain_diff.array})

    p = figure(x_axis_type="datetime", plot_width=800, plot_height=350)
    p.title.text = "Error in same-day nowcast of 7-day rolling average of positive tests"
    p.title.align = "center"
    p.title.text_font_size = "18px"
    p.line('Date', 'Value', source=source_gross_diff, line_width=3, legend_label="Gross", line_color=Spectral10[1])
    p.line('Date', 'Value', source=source_nowcast_chain_diff, line_width=3, line_dash="solid", legend_label="Nowcast (β=0.0)", line_color=Spectral10[9])
    p.line('Date', 'Value', source=source_nowcast_chain_0_2_diff, line_width=3, line_dash="solid", legend_label="Nowcast (β=0.2)", line_color=Spectral10[2])

    p.xaxis.formatter = DatetimeTickFormatter(days="%d/%b", months="%d/%b", hours="%d/%b", minutes="%d/%b")
    p.yaxis.axis_label = "Error in positive tests"
    p.legend.location = "top_left"

    export_png(p, filename=statistics_repository.folder + r"plots\{country}\COVID-19_daily_cases_nowcast_error.png".format(country=statistics_repository.country_code))
