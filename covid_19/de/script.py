import sys
from covid_19.de.updating import update_files, update_measures
from covid_19.de.dataretrieval import get_measures, RkiAndGitHubRepositoryWithCaching, StatisticsRepository, REPORTING_LAG
from covid_19.plotting import generate_plot_national_cases_per_day_chainladder, generate_plots_chainladder
import datetime


if __name__ == "__main__":
    folder = sys.argv[1]
    date_to_run = None
    if len(sys.argv) == 3:
        date_to_run = sys.argv[2]

    dt_today = datetime.datetime.today().date()
    repository = RkiAndGitHubRepositoryWithCaching(dt_today)
    if date_to_run is None:
        try:
            _ = repository.get_dataset(dt_today)
        except:
            sys.exit(0)

    statistics_repository = StatisticsRepository(folder)

    update_files(folder, repository, date_to_run)
    update_measures(get_measures(folder), folder, repository, date_to_run).to_csv(folder + r"data\de\COVID-19_measures.csv")
    generate_plot_national_cases_per_day_chainladder(repository, statistics_repository, 30, REPORTING_LAG)
    generate_plots_chainladder(repository, statistics_repository, datetime.date(2020, 8, 1), 21, REPORTING_LAG)
