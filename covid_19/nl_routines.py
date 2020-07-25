from dataretrieval import update_files
from plotting import generate_plot
import sys


if __name__ == "__main__":
    folder = sys.argv[1]
    update_files(folder)
    generate_plot(folder, 30)
    