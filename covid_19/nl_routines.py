from dataretrieval import get_latest_rivm_file

if __name__ == "__main__":
    df = get_latest_rivm_file()
    df.to_csv(r".\data\COVID-19_casus_landelijk.csv")

