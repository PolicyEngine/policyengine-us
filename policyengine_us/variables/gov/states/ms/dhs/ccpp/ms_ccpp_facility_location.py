from policyengine_us.model_api import *


class MSCCPPFacilityLocation(Enum):
    METRO = "Metro"
    NON_METRO = "Non-metro"


class ms_ccpp_facility_location(Variable):
    value_type = Enum
    entity = Household
    possible_values = MSCCPPFacilityLocation
    default_value = MSCCPPFacilityLocation.NON_METRO
    definition_period = YEAR
    label = "Mississippi CCPP facility metro or non-metro location"
    defined_for = StateCode.MS
    # The metro / non-metro split is a Market Rate Survey rate-table dimension
    # (Table 1 and Table 2 disaggregate rates by metro status), not a manual rule.
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2024/06/Mississippi-Child-Care-Market-Rate-Survey-2024.pdf#page=9"

    def formula(household, period, parameters):
        # CCPP rates vary by the facility's metro / non-metro location. We don't
        # track the child care facility's location at the moment, so we use the
        # household's county as a proxy for the facility location.
        county = household("county_str", period)
        p = parameters(period).gov.states.ms.dhs.ccpp.geography
        is_metro = np.isin(county, p.metro_counties)
        return where(
            is_metro,
            MSCCPPFacilityLocation.METRO,
            MSCCPPFacilityLocation.NON_METRO,
        )
