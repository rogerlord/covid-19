import sys
from covid_19.nl.dataretrieval import get_measures, RivmAndGitHubRepositoryWithCaching
from covid_19.nl.plotting import generate_plot_daily_cases_per_ggd_region, \
    generate_plot_heatmap, generate_plot_national_cases_per_day_chainladder, generate_plots_chainladder
from covid_19.nl.updating import update_files, update_measures
import datetime


if __name__ == "__main__":
    folder = sys.argv[1]
    date_to_run = None
    if len(sys.argv) == 3:
        date_to_run = sys.argv[2]

    repository = RivmAndGitHubRepositoryWithCaching(datetime.datetime.today())

    update_files(folder, repository, date_to_run)
    update_measures(get_measures(folder), folder, repository, date_to_run).to_csv(folder + r"data\nl\COVID-19_measures.csv")
    generate_plot_national_cases_per_day_chainladder(folder, repository, 30)
    generate_plots_chainladder(folder, repository, datetime.date(2020, 8, 1), 21)
    generate_plot_daily_cases_per_ggd_region(folder, "gross")
    generate_plot_heatmap(folder, repository)
