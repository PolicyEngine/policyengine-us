# Florida School Readiness Program provider reimbursement rates (daily, by county).
# Sources (the two published fiscal years carry IDENTICAL rates -- see "Effective
# window"), both incorporated by reference under Fla. Admin. Code 6M-4.500:
#  - FY2025-26: "School Readiness Reimbursement Rates, Fiscal Year 2025-2026"
#    (SPB 2502, Florida Senate Committee on Appropriations, April 3, 2025).
#    https://www.flsenate.gov/PublishedContent/Session/2025/Conference/9/RelatedDocument/School%20Readiness%20Reimbursement%20Rates_1411.pdf
#  - FY2026-27: "School Readiness Reimbursement Rates, Fiscal Year 2026-2027"
#    (Conference Report for HB 5001E, Florida House Budget Committee, May 26, 2026).
#    https://www.flsenate.gov/PublishedContent/Session/2026E/Conference/11/RelatedDocument/School%20Readiness%20Reimbursement%20Rates%205-26-26_1750.pdf
# One table per county (all 67); each is keyed by unit of care (full-time/part-time),
# care level (infant ... school age), and provider type.
#
# Effective window: Florida's fiscal year runs July 1 - June 30. These rates apply
# to BOTH FY2025-26 (2025-07-01 - 2026-06-30) and FY2026-27 (2026-07-01 - 2027-06-30):
# the FY2026-27 schedule carries the FY2025-26 amounts forward unchanged -- verified
# byte-identical (0 of 2,814 cells differ) -- so a single CSV (fy2025_26.csv) covers
# both years. The program is modeled from 2025-10-01 (the SMI copay-scale effective
# date), which falls inside this window. If a future fiscal year ever publishes
# DIFFERENT rates, add it as fy<YYYY>.csv and select by the July 1 fiscal-year
# boundary (fy = year + (1 if month >= 7 else 0)) in get_reimbursement_rates.
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

    FY2025-26 and FY2026-27 are both published and carry identical rates (see the
    module header), so the single fy2025_26.csv covers both fiscal years. If a
    future fiscal year publishes different rates, add it as fy<YYYY>.csv and
    select by the July 1 boundary here. Returns a DataFrame with columns
    county, provider_type, care_level, unit, rate.
    """
    return pd.read_csv(
        FOLDER / "fy2025_26.csv",
        dtype={k: str for k in _MERGE_KEYS},
    )
