from policyengine_us.model_api import *


class MECCAPRegion(Enum):
    REGION_1 = "Region 1"
    REGION_2 = "Region 2"
    KENNEBEC = "Kennebec"
    KNOX_WALDO = "Knox/Waldo"
    PENOBSCOT = "Penobscot"


class me_ccap_region(Variable):
    value_type = Enum
    entity = Household
    possible_values = MECCAPRegion
    default_value = MECCAPRegion.REGION_2
    definition_period = MONTH
    defined_for = StateCode.ME
    label = "Maine CCAP geographic region"
    reference = (
        "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=25",
        "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/July%206%202024%20Market%20Rates_5_0.pdf",
    )

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.me.dhhs.ccap
        is_region_1 = np.isin(county, p.region_1_counties)
        is_kennebec = np.isin(county, p.kennebec_counties)
        is_knox_waldo = np.isin(county, p.knox_waldo_counties)
        is_penobscot = np.isin(county, p.penobscot_counties)
        return select(
            [is_region_1, is_kennebec, is_knox_waldo, is_penobscot],
            [
                MECCAPRegion.REGION_1,
                MECCAPRegion.KENNEBEC,
                MECCAPRegion.KNOX_WALDO,
                MECCAPRegion.PENOBSCOT,
            ],
            default=MECCAPRegion.REGION_2,
        )
