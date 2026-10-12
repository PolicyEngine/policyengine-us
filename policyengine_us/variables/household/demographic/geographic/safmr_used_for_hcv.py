from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hud.fmr import small_area_fair_market_rents

# Metros where HUD mandates Small Area FMR use for Housing Choice Voucher
# payment standards (HUD Notice PIH 2023-32 Appendix A; 24 CFR 888.113) — the
# Texas members: Dallas, Fort Worth-Arlington, and San Antonio (2018 cohort)
# plus Beaumont-Port Arthur (2023 expansion). Kansas members: Kansas City,
# MO-KS and Wichita, KS (2023 expansion, effective 2025-01-01). Houston is NOT
# designated, so its SAFMR is not its HCV basis. The names below match the
# `hud_area_name` column in small_area_fair_market_rents.csv, which suffixes
# each metro with its 2-letter state (e.g. "Dallas, TX", "Wichita, KS"). A
# ZIP's SAFMR is its payment-
# standard basis only if its metro is listed here, so raw SAFMR data never
# leaks into HCV.
SAFMR_HCV_DESIGNATED_METROS = [
    "Beaumont-Port Arthur, TX",
    "Dallas, TX",
    "Fort Worth, TX",
    "Kansas City, KS",
    "San Antonio, TX",
    "Wichita, KS",
]
SAFMR_HCV_ZIPS = frozenset(
    small_area_fair_market_rents.loc[
        small_area_fair_market_rents["hud_area_name"].isin(SAFMR_HCV_DESIGNATED_METROS),
        "zip_code",
    ]
)


class safmr_used_for_hcv(Variable):
    value_type = bool
    entity = Household
    label = "Small area fair market rent used for purposes of the Housing Choice Voucher Program"
    documentation = (
        "Whether the household's ZIP code falls in a metropolitan area where HUD "
        "mandates Small Area FMR use as the Housing Choice Voucher payment "
        "standard basis."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/888.113"

    def formula(household, period, parameters):
        zip_code = household("zip_code", period)
        zips = pd.Series(np.asarray(zip_code).astype(str)).str.zfill(5)
        return zips.isin(SAFMR_HCV_ZIPS).to_numpy()
