import sys
from covid_19.nl.dataretrieval import get_measures
from covid_19.nl.plotting import generate_plot_national_cases_per_day, generate_plot_daily_cases_per_ggd_region, \
    generate_plot_heatmap
from covid_19.nl.updating import update_files, update_measures


if __name__ == "__main__":
    folder = sys.argv[1]
    update_files(folder)
    update_measures(get_measures(folder), folder).to_csv(folder + r"data\nl\COVID-19_measures.csv")
    generate_plot_national_cases_per_day(folder, 30)
    generate_plot_daily_cases_per_ggd_region(folder, "gross")
    generate_plot_heatmap(folder)
