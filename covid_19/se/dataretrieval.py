import pandas as pd


def get_daily_cases_historical(date_file):
    # Han Lin Yap (codler) kindly stores the history of the Folkhälsomyndigheten files in his GitHub repository
    uri = "https://github.com/codler/sweden-coronavirus/blob/master/folkhalsomyndigheten/"
    file_name_start = "Folkhalsomyndigheten_Covid19_"
    df_folkhalsomyndigheten = pd.read_excel(uri + file_name_start + date_file.strftime("%Y-%m-%d") + ".xlsx?raw=true",
                                            sheet_name="Antal per dag region")
    df_folkhalsomyndigheten["Statistikdatum"] = pd.to_datetime(df_folkhalsomyndigheten["Statistikdatum"],
                                                               format="%d-%m-%Y")
    df_folkhalsomyndigheten.set_index("Statistikdatum", inplace=True)
    return df_folkhalsomyndigheten
