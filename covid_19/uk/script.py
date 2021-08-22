import sys
from covid_19.uk.updating import update_files
from covid_19.uk.dataretrieval import UkGovRepository
import datetime


def run_script(folder, date_to_run=None, repository=None):



if __name__ == "__main__":
    folder = sys.argv[1]
    date_to_run = None
    if len(sys.argv) == 3:
        date_to_run = sys.argv[2]

    dt_today = datetime.datetime.today().date()
    repository = UkGovRepository(dt_today)
    if date_to_run is None:
        try:
            _ = repository.get_dataset(dt_today)
        except:
            sys.exit(0)

    update_files(folder, repository, date_to_run)
    update_measures(get_measures(folder), folder, repository, date_to_run).to_csv(folder + r"data\de\COVID-19_measures.csv")

    generate_plot_national_cases_per_day_chainladder(repository, statistics_repository, 30, REPORTING_LAG)
    generate_plots_chainladder(repository, statistics_repository, datetime.date(2020, 8, 1), 21, REPORTING_LAG)

