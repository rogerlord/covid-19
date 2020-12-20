import sys
from covid_19.de.updating import update_files


if __name__ == "__main__":
    folder = sys.argv[1]
    date_to_run = None
    if len(sys.argv) == 3:
        date_to_run = sys.argv[2]

    update_files(folder, date_to_run)
