import sys
from covid_19.uk.updating import update_files
from covid_19.uk.dataretrieval import UkGovRepository
import datetime


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
