import sys
from covid_19.de.updating import update_files, update_measures
from dataretrieval import get_measures, RkiAndGitHubRepositoryWithCaching
import datetime


if __name__ == "__main__":
    folder = sys.argv[1]
    date_to_run = None
    if len(sys.argv) == 3:
        date_to_run = sys.argv[2]

    repository = RkiAndGitHubRepositoryWithCaching(datetime.datetime.today())

    update_files(folder, repository, date_to_run)
    update_measures(get_measures(folder), folder, repository, date_to_run).to_csv(folder + r"data\de\COVID-19_measures.csv")
