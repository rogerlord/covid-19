import datetime

import numpy as np
import pandas as pd


def create_lagged_values_differences(lagged_array):
    num_rows = lagged_array.shape[0]
    num_cols = lagged_array.shape[1]

    differences_array = np.zeros((num_rows, num_cols))
    for i in range(0, num_rows):
        differences_array[i, 0] = lagged_array[i, 0]
        for j in range(1, num_cols):
            differences_array[i, j] = lagged_array[i, j] - lagged_array[i, j - 1]

    return differences_array


def recreate_lagged_values(df_lagged: pd.DataFrame, dt: datetime.date) -> pd.DataFrame:
    """

    Args:
        df_lagged (pandas.DataFrame): Dataframe with observations at multiple lags - indexed by observation date, columns equal to observations at lags (0 = same day, 1 = after one day, etc.)
        dt (datetime.date): The date as of which the user wants to recreate the dataframe with lagged values.

    Returns:
        pandas.DataFrame: A dataframe with observations at multiple lags as observed at date dt.
    """
    df = df_lagged.copy()
    first_date = min(df.index).date()
    df = df[first_date:dt]
    num_columns = len(df.columns)
    for i in range(1, num_columns):
        for j in range(i + 1, num_columns + 1):
            df.iat[-i, j - 1] = np.nan
    return df
