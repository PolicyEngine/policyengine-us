from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hud.fmr import small_area_fair_market_rents

# Metros where HUD mandates Small Area FMR use for Housing Choice Voucher
# payment standards (2016 SAFMR Final Rule; 24 CFR 888.113) — the Texas
# members. A ZIP's SAFMR is its HCV payment-standard basis only if its metro is
# listed here, so raw SAFMR data added for other uses never leaks into HCV.
SAFMR_HCV_DESIGNATED_METROS = ["Dallas", "Fort Worth", "Houston", "San Antonio"]
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
    definition_period = YEAR

    def formula(household, period, parameters):
        zip_code = household("zip_code", period)
        zips = pd.Series(np.asarray(zip_code).astype(str)).str.zfill(5)
        return zips.isin(SAFMR_HCV_ZIPS).to_numpy()
