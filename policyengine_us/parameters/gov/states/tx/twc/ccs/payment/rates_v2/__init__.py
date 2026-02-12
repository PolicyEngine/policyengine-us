import pandas as pd
from pathlib import Path

FOLDER = Path(__file__).parent

# Column name -> (age_group_enum_name, schedule_enum_name)
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


def _build_lookup(csv_path):
    """Build a nested dict: region -> provider_type -> rating -> age_group -> schedule -> rate."""
    df = pd.read_csv(csv_path)
    lookup = {}
    for _, row in df.iterrows():
        region = row["region"]
        ptype = row["provider_type"]
        rating = row["provider_rating"]
        if region not in lookup:
            lookup[region] = {}
        if ptype not in lookup[region]:
            lookup[region][ptype] = {}
        if rating not in lookup[region][ptype]:
            lookup[region][ptype][rating] = {}
        for col, (age_group, schedule) in COLUMN_MAP.items():
            if age_group not in lookup[region][ptype][rating]:
                lookup[region][ptype][rating][age_group] = {}
            lookup[region][ptype][rating][age_group][schedule] = float(
                row[col]
            )
    return lookup


bcy26_rates = _build_lookup(FOLDER / "bcy26.csv")
