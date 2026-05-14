from policyengine_us.model_api import *


class SCCCAPGeography(Enum):
    URBAN = "Urban"
    RURAL = "Rural"


class sc_ccap_geography(Variable):
    value_type = Enum
    entity = Household
    possible_values = SCCCAPGeography
    default_value = SCCCAPGeography.RURAL
    definition_period = YEAR
    label = "South Carolina CCAP urban or rural county designation"
    defined_for = StateCode.SC
    reference = "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=198"

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.sc.dss.ccap.geography
        is_urban = np.isin(county, p.urban_counties)
        return where(
            is_urban,
            SCCCAPGeography.URBAN,
            SCCCAPGeography.RURAL,
        )
