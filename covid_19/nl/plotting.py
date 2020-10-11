from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.io import export_png
from bokeh.models import DatetimeTickFormatter
from bokeh.palettes import Spectral10
from covid_19.nl.dataretrieval import get_cases_per_day_from_file, get_measures, get_latest_rivm_file
from covid_19.nl.forecasting import forecast_daily_cases
from covid_19.nl.demography import get_ggd_regions, get_ggd_regions_geographical_boundaries, \
    get_population_per_ggd_region
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns


def generate_plot_national_cases_per_day(folder, show_only_last):
    df_daily = get_cases_per_day_from_file(folder)
    df_updated = forecast_daily_cases(folder, maximum_lag=14)
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
        ds[ggd_region] = df_measures[measure + "_" + ggd_region].rolling(window=7).sum().iloc[-1]

    df_data = pd.DataFrame.from_dict(data={"Municipal_health_service": list(ds.keys()), measure: list(ds.values())})
    df_data = pd.merge(ggd_regions, df_data, left_on="Municipal_health_service", right_on="Municipal_health_service")
    df_data = pd.merge(get_ggd_regions_geographical_boundaries(), df_data, left_on="statcode", right_on="statcode")
    population_per_ggd_region = get_population_per_ggd_region()
    df_data["Inhabitants"] = df_data["statcode"].map(lambda x: population_per_ggd_region[x])
    df_data["Infections_per_100K"] = df_data[measure] / df_data["Inhabitants"] * 100_000.0

    measure_for_country = df_measures[measure+"_nl"].rolling(window=7).sum().iloc[-1]
    inhabitants = sum(population_per_ggd_region.values())
    measure_for_country *= 100_000.0 / inhabitants

    return measure_for_country, df_data


def get_custom_colourmap():
    colours = ["yellow", "orange", "red", "darkred", "maroon", "black"]
    nodes = np.array([0.0, 25.0, 50.0, 100.0, 125.0, 150.0]) / 200.0
    return LinearSegmentedColormap.from_list("customcmap", list(zip(nodes, colours)))


def generate_plot_daily_cases_per_ggd_region(folder, measure):
    measure_for_country, df_data = generate_data_frame_for_plot_daily_cases_per_ggd_region(folder, measure)

    matplotlib.rcParams["text.color"] = 'white'
    fig = df_data.plot(column="Infections_per_100K", figsize=(10, 8), cmap=get_custom_colourmap(), legend=True,
                       vmin=0.0, vmax=150.0, edgecolor="gray", linewidth=0.25)
    [l.set_family("Arial") for l in fig.figure.axes[1].yaxis.get_ticklabels()]
    df_data["coords"] = df_data["geometry"].apply(lambda x: x.representative_point().coords[:])
    df_data["coords"] = [coords[0] for coords in df_data["coords"]]

    for idx, row in df_data.iterrows():
        plt.annotate(text=round(row["Infections_per_100K"], 1), xy=row["coords"], horizontalalignment="center",
                     fontname="Arial", fontsize=10)

    plt.axis("off")
    _ = plt.title(
        'New COVID-19 infections per 7 days per 100,000 inhabitants \n NL overall average: {measure_for_country}'.format(measure_for_country=round(measure_for_country, 1)), fontname="Arial", fontsize=13)

    plt.savefig(folder + r"plots\nl\COVID-19_daily_cases_per_ggd_region_plot.jpg")
    plt.close()


def generate_data_frame_for_plot_heatmap():
    df_rivm = get_latest_rivm_file()
    df_filtered = df_rivm[(df_rivm["Agegroup"] != "Unknown") & (df_rivm["Agegroup"] != "<50")]
    df_filtered = df_filtered[["Agegroup", "Date_statistics"]]
    df_filtered = df_filtered.reset_index().drop(columns="Date_file")
    df_filtered = df_filtered.groupby(["Agegroup", "Date_statistics"]).size()
    df_filtered.name = "Count"
    df_filtered = df_filtered.reset_index()
    df_filtered["Percent"] = df_filtered.groupby('Date_statistics')['Count'].transform(lambda x: x / sum(x))
    df_filtered = df_filtered.set_index(["Agegroup", "Date_statistics"])
    age_groups = ['90+', '80-89', '70-79', '60-69', '50-59', '40-49', '30-39', '20-29', '10-19', '0-9']
    date_range = pd.date_range(min(df_rivm["Date_statistics"]).date(), max(df_rivm["Date_statistics"]).date())
    df_filtered = df_filtered.reindex(
        pd.MultiIndex.from_product([age_groups, date_range], names=["Agegroup", "Date"]),
        fill_value=0.0).reset_index().pivot("Agegroup", "Date", "Percent")
    df_filtered.sort_index(level=0, ascending=False, inplace=True)
    df_filtered = df_filtered.rename(
        columns=dict(zip(df_filtered.columns, list(map(lambda x: x.strftime("%d/%b/%y"), df_filtered.columns)))))
    return df_filtered


def generate_plot_heatmap(folder):
    df_data = generate_data_frame_for_plot_heatmap()
    ax = sns.heatmap(df_data, cmap="YlOrRd", xticklabels=14, vmax=0.35)
    _ = ax.set_ylabel("Age group")
    _ = ax.text(
        -0.1,
        -0.35,
        f"Each pixel represents a 1-day time period and age group\n"
        f"Intensity indicates the % of infections in the age group\n"
        f"relative to all cases reported on that day\n",
        transform=ax.transAxes,
        verticalalignment="top",
    )
    ax.figure.suptitle(f"Heatmap of COVID-19 cases in the Netherlands")
    cbar = ax.collections[0].colorbar
    cbar.set_ticks(cbar.get_ticks())
    cbar.set_ticklabels(list(map(lambda x: "{:.0%}".format(x), cbar.get_ticks())))
    ax.figure.savefig(folder + r"plots\nl\COVID-19_heatmap_plot.jpg", bbox_inches='tight')
    plt.close()
