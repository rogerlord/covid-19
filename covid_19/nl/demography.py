import cbsodata
import pandas as pd
import os


def get_population_per_ggd_region():
    # Table 84721NED gives information about regions within the Netherlands
    # See: https://www.cbs.nl/nl-nl/cijfers/detail/84721NED
    cbs_data = cbsodata.get_data('84721NED', select=['RegioS', 'Code_14', 'Inwonertal_52'])
    cbs_df = pd.DataFrame(cbs_data).groupby("Code_14").sum()
    cbs_df.index = cbs_df.index.str.strip()
    return cbs_df.to_dict()["Inwonertal_52"]


def get_ggd_regions():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.join(dir_path, '../../config/nl/ggd_regions.csv')
    return pd.read_csv(file_name)


def get_ggd_regions_geographical_boundaries():
    import geopandas as gpd
    geodata_url = 'http://geodata.nationaalgeoregister.nl/cbsgebiedsindelingen/wfs?request=GetFeature&service=WFS&version=2.0.0&typeName=cbs_ggdregio_2019_gegeneraliseerd&outputFormat=json'
    return gpd.read_file(geodata_url)
