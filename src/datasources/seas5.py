from typing import List, Optional

import pandas as pd

from src.utils import db_utils

SEAS5_QUERY_STRING = """
SELECT *
FROM public.seas5
WHERE EXTRACT(MONTH FROM valid_date) IN ({valid_months})
  AND EXTRACT(MONTH FROM issued_date) IN ({issue_months})
  AND (pcode IN ({pcodes}) OR iso3 = {iso3})
  AND adm_level = {adm_level}
ORDER BY issued_date, valid_date, pcode;
"""


def load_seas5(
    valid_months: Optional[List[int]] = range(1, 13),
    issue_months: Optional[List[int]] = range(1, 13),
    adm_level: int = 1,
    pcodes: Optional[List[str]] = None,
    iso3: Optional[str] = None,
    verbose: bool = False,
):
    if not pcodes and not iso3:
        raise ValueError("Specify at least one of pcodes or iso3.")

    engine = db_utils.get_engine()
    query = SEAS5_QUERY_STRING.format(
        valid_months=",".join([str(month) for month in valid_months]),
        issue_months=",".join([str(month) for month in issue_months]),
        pcodes=(
            ",".join([f"'{pcode}'" for pcode in pcodes]) if pcodes else "NULL"
        ),
        iso3=f"'{iso3.upper()}'" if iso3 else "NULL",
        adm_level=adm_level,
    )
    if verbose:
        print(query)
    df = pd.read_sql(query, engine, parse_dates=["valid_date", "issued_date"])
    df["iso3"] = df["iso3"].str.lower()
    df = df.rename(columns={"pcode": f"ADM{adm_level}_PCODE"})
    return df
