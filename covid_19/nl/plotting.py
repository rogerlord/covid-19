from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.io import export_png
from bokeh.models import DatetimeTickFormatter
from bokeh.palettes import Spectral10
from covid_19.nl.dataretrieval import get_cases_per_day_from_file, get_measures
from covid_19.nl.forecasting import forecast_daily_cases
from covid_19.nl.demography import get_ggd_regions, get_ggd_regions_geographical_boundaries, \
    get_population_per_ggd_region
import pandas as pd
import matplotlib.pyplot as plt


def generate_plot_national_cases_per_day(folder, show_only_last):
    df_daily = get_cases_per_day_from_file(folder)
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


def generate_data_frame_for_plot_daily_cases_per_ggd_region(folder, measure):
    ggd_regions = get_ggd_regions()
    df_measures = get_measures(folder)
    ds = dict()
    for ggd_region in ggd_regions["Municipal_health_service"]:
        ds[ggd_region] = df_measures[measure + "_" + ggd_region].rolling(window=7).mean().iloc[-1]

    df_data = pd.DataFrame.from_dict(data={"Municipal_health_service": list(ds.keys()), measure: list(ds.values())})
    df_data = pd.merge(ggd_regions, df_data, left_on="Municipal_health_service", right_on="Municipal_health_service")
    df_data = pd.merge(get_ggd_regions_geographical_boundaries(), df_data, left_on="statcode", right_on="statcode")
    population_per_ggd_region = get_population_per_ggd_region()
    df_data["Inhabitants"] = df_data["statcode"].map(lambda x: population_per_ggd_region[x])
    df_data["Infections_per_100K"] = df_data[measure] / df_data["Inhabitants"] * 100_000.0

    measure_for_country = df_measures[measure+"_nl"].rolling(window=7).mean().iloc[-1]
    inhabitants = sum(population_per_ggd_region.values())
    measure_for_country *= 100_000.0 / inhabitants

    return measure_for_country, df_data


def generate_plot_daily_cases_per_ggd_region(folder, measure):
    measure_for_country, df_data = generate_data_frame_for_plot_daily_cases_per_ggd_region(folder, measure)
    fig = df_data.plot(column="Infections_per_100K", figsize=(10,8), cmap="YlOrRd", legend=True, vmax=50.0/7,
                       edgecolor="gray", linewidth=0.25)
    [l.set_family("Arial") for l in fig.figure.axes[1].yaxis.get_ticklabels()]
    df_data["coords"] = df_data["geometry"].apply(lambda x: x.representative_point().coords[:])
    df_data["coords"] = [coords[0] for coords in df_data["coords"]]

    for idx, row in df_data.iterrows():
        plt.annotate(text=round(row["Infections_per_100K"], 1), xy=row["coords"], horizontalalignment="center",
                     fontname="Arial", fontsize=10)

    plt.axis("off")
    _ = plt.title(
        '7-day average of new COVID-19 infections per 100,000 inhabitants \n NL overall average: {measure_for_country}'.format(measure_for_country=round(measure_for_country, 1)), fontname="Arial", fontsize=13)

    plt.savefig(folder + r"plots\nl\COVID-19_daily_cases_per_ggd_region_plot.png")
