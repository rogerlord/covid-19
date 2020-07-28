import sys
from covid_19.nl.plotting import generate_plot
from covid_19.nl.updating import update_files


if __name__ == "__main__":
    folder = sys.argv[1]
    update_files(folder)
    generate_plot(folder, 30)
