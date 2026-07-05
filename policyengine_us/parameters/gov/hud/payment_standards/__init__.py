import pandas as pd
from pathlib import Path

FOLDER = Path(__file__).parent

# PHA-published Housing Choice Voucher payment standards at the ZIP-code level,
# indexed by (zip_code, year, bedrooms). These are the standards a public
# housing authority has actually adopted (already reflecting its choice within
# HUD's 90-110 percent of FMR band), so they feed `pha_payment_standard`
# directly and take precedence over Small Area FMRs and county FMRs.
#
# Currently scoped to the Texas Department of Housing and Community Affairs
# (TDHCA) service area (the counties without their own local housing
# authority). Other states' schedules can append to the same CSV.
zip_code_payment_standards = pd.read_csv(
    FOLDER / "zip_code_payment_standards.csv",
    dtype={"zip_code": str},
)
zip_code_payment_standards["zip_code"] = (
    zip_code_payment_standards["zip_code"].str.strip().str.zfill(5)
)
available_payment_standard_years = sorted(
    zip_code_payment_standards["year"].unique().tolist()
)


def nearest_payment_standard_year(year: int) -> int:
    prior_years = [
        candidate for candidate in available_payment_standard_years if candidate <= year
    ]
    if prior_years:
        return max(prior_years)
    return min(available_payment_standard_years)
