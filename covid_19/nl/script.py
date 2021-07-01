import sys
from covid_19.nl.dataretrieval import get_measures, RivmAndGitHubRepositoryWithCaching, StatisticsRepository
from covid_19.nl.plotting import generate_plot_daily_cases_per_ggd_region, \
    generate_plot_heatmap
from covid_19.plotting import generate_plot_national_cases_per_day_chainladder, generate_plots_chainladder
from covid_19.nl.updating import update_files, update_measures
import datetime


def run_script(folder, date_to_run = None):
    dt_today = datetime.datetime.today().date()
    repository = RivmAndGitHubRepositoryWithCaching(dt_today)
    if date_to_run is None:
        try:
            _ = repository.get_dataset(dt_today)
        except:
            sys.exit(0)
        date_to_run = datetime.datetime.today().date()

    statistics_repository = StatisticsRepository(folder)

    update_files(folder, repository, date_to_run)
    update_measures(get_measures(folder), folder, repository, date_to_run).to_csv(folder + r"data\nl\COVID-19_measures.csv")
    generate_plot_national_cases_per_day_chainladder(repository, statistics_repository, 30)
    generate_plots_chainladder(repository, statistics_repository, datetime.date(2020, 8, 1), 21)
    generate_plot_daily_cases_per_ggd_region(folder, "gross")
    generate_plot_heatmap(folder, repository, date_to_run)


if __name__ == "__main__":
    folder = sys.argv[1]
    date_to_run = None
    if len(sys.argv) == 3:
        date_to_run = sys.argv[2]

    run_script(folder, date_to_run)
