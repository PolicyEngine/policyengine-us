# Sources:
# BCY25: https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy25-board-max-provider-payment-rates-8-age-groups-twc.pdf
# BCY26: https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy26-board-max-provider-payment-rates-twc.pdf

import pandas as pd
from functools import lru_cache
from pathlib import Path

FOLDER = Path(__file__).parent
_AVAILABLE_YEARS = sorted(
    int(f.stem.replace("bcy", "")) for f in FOLDER.glob("bcy*.csv")
)

# CSV column name -> (age_group enum name, schedule enum name)
COLUMN_MAP = {
    "age_0_11m_ft": ("AGE_0_11_MONTHS", "FULL_TIME"),
    "age_0_11m_pt": ("AGE_0_11_MONTHS", "PART_TIME"),
    "age_12_17m_ft": ("AGE_12_17_MONTHS", "FULL_TIME"),
    "age_12_17m_pt": ("AGE_12_17_MONTHS", "PART_TIME"),
    "age_18_23m_ft": ("AGE_18_23_MONTHS", "FULL_TIME"),
    "age_18_23m_pt": ("AGE_18_23_MONTHS", "PART_TIME"),
    "age_2yr_ft": ("AGE_2_YEARS", "FULL_TIME"),
    "age_2yr_pt": ("AGE_2_YEARS", "PART_TIME"),
    "age_3yr_ft": ("AGE_3_YEARS", "FULL_TIME"),
    "age_3yr_pt": ("AGE_3_YEARS", "PART_TIME"),
    "age_4yr_ft": ("AGE_4_YEARS", "FULL_TIME"),
    "age_4yr_pt": ("AGE_4_YEARS", "PART_TIME"),
    "age_5yr_ft": ("AGE_5_YEARS", "FULL_TIME"),
    "age_5yr_pt": ("AGE_5_YEARS", "PART_TIME"),
    "age_6_13yr_ft": ("AGE_6_13_YEARS", "FULL_TIME"),
    "age_6_13yr_pt": ("AGE_6_13_YEARS", "PART_TIME"),
    "age_4yr_bt": ("AGE_4_YEARS", "BLENDED"),
    "age_5yr_bt": ("AGE_5_YEARS", "BLENDED"),
    "age_6_13yr_bt": ("AGE_6_13_YEARS", "BLENDED"),
}

KEY_COLS = ["region", "provider_type", "provider_rating"]


def _load_long(csv_path):
    """Load a BCY CSV and melt into long form with columns:
    region, provider_type, provider_rating, age_group, schedule, rate
    """
    df = pd.read_csv(csv_path)
    records = []
    for col, (age_group, schedule) in COLUMN_MAP.items():
        subset = df[KEY_COLS + [col]].copy()
        subset = subset.rename(columns={col: "rate"})
        subset["age_group"] = age_group
        subset["schedule"] = schedule
        records.append(subset)
    long = pd.concat(records, ignore_index=True)
    long = long.dropna(subset=["rate"])
    return long


@lru_cache(maxsize=None)
def get_rates(bcy_year):
    year = int(bcy_year)
    if year > _AVAILABLE_YEARS[-1]:
        year = _AVAILABLE_YEARS[-1]
    return _load_long(FOLDER / f"bcy{year}.csv")
