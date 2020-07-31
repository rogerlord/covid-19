import sys
from dataretrieval import get_measures
from plotting import generate_plot_national_cases_per_day, generate_plot_daily_cases_per_ggd_region
from updating import update_files, update_measures


if __name__ == "__main__":
    folder = sys.argv[1]
    update_files(folder)
    update_measures(get_measures(folder)).to_csv(folder + r"data\nl\COVID-19_measures.csv")
    generate_plot_national_cases_per_day(folder, 30)
    generate_plot_daily_cases_per_ggd_region(folder, "gross_21")
