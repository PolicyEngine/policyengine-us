# Florida School Readiness Program provider reimbursement rates (daily, by county).
# Source: "School Readiness Reimbursement Rates, Fiscal Year 2025-2026" (SPB 2502,
# Florida Senate Committee on Appropriations, April 3, 2025), incorporated by
# reference under Fla. Stat. s. 1002.895 / Fla. Admin. Code 6M-4.500. One table
# per county (all 67); each table is keyed by unit of care (full-time/part-time),
# care level (infant ... school age), and provider type.
#
# Stored as a CSV (long form) rather than nested YAML because the table is large
# (67 counties x 2 units x 7 care levels x 3 provider types = 2,814 daily rates).
# Mirrors the Texas CCS CSV-rate-table pattern.

import pandas as pd
from functools import lru_cache
from pathlib import Path

FOLDER = Path(__file__).parent

# CSV columns: county, provider_type, care_level, unit, rate
# - county        : county_enum member name (e.g. MIAMI_DADE_COUNTY_FL)
# - provider_type : fl_sr_provider_type enum member name
# - care_level    : fl_sr_care_level enum member name
# - unit          : fl_sr_time_category enum member name (FULL_TIME / PART_TIME)
# - rate          : daily reimbursement rate in USD
_MERGE_KEYS = ["county", "provider_type", "care_level", "unit"]


@lru_cache(maxsize=None)
def get_reimbursement_rates(fiscal_year=2026):
    """Return the long-form daily reimbursement-rate table for a fiscal year.

    Only FY2025-26 is currently published; later years can be added as
    fy<YYYY>.csv files and selected here. Returns a DataFrame with columns
    county, provider_type, care_level, unit, rate.
    """
    return pd.read_csv(
        FOLDER / "fy2025_26.csv",
        dtype={k: str for k in _MERGE_KEYS},
    )
