import pandas as pd

from src.constants import ISO3
from src.utils import db_utils


def load_era5(verbose: bool = False):
    engine = db_utils.get_engine()
    query = f"""
    SELECT *
    FROM public.era5
    WHERE iso3 = {ISO3.upper()}
    AND admin_level = 1
    """
    if verbose:
        print(query)
    df = pd.read_sql(query, engine, parse_dates=["valid_date"])
    df["iso3"] = df["iso3"].str.lower()
    return df
