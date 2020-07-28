import cbsodata
import pandas as pd


def get_population_per_ggd_region():
    # Table 84721NED gives information about regions within the Netherlands
    # See: https://www.cbs.nl/nl-nl/cijfers/detail/84721NED
    cbs_data = cbsodata.get_data('84721NED', select=['RegioS', 'Code_14', 'Inwonertal_50'])
    cbs_df = pd.DataFrame(cbs_data).groupby("Code_14").sum()
    cbs_df.index = cbs_df.index.str.strip()
    return cbs_df.to_dict()["Inwonertal_50"]
