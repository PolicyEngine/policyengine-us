from policyengine_us.model_api import *


class CTC4KRegion(Enum):
    EASTERN = "Eastern"
    NORTH_CENTRAL = "North Central"
    NORTHWEST = "Northwest"
    SOUTH_CENTRAL = "South Central"
    SOUTHWEST = "Southwest"


class ct_c4k_region(Variable):
    value_type = Enum
    entity = Household
    possible_values = CTC4KRegion
    default_value = CTC4KRegion.NORTH_CENTRAL
    definition_period = MONTH
    defined_for = StateCode.CT
    label = "Connecticut Care 4 Kids geographic region"
    reference = "https://www.ctoec.org/care-4-kids/c4k-providers/c4k-rates/"

    def formula(household, period, parameters):
        # NOTE: Uses county approximation; CT C4K regions are town-based.
        county = household("county_str", period)
        p = parameters(period).gov.states.ct.oec.c4k.region

        eastern = np.isin(county, p.eastern)
        northwest = np.isin(county, p.northwest)
        south_central = np.isin(county, p.south_central)
        southwest = np.isin(county, p.southwest)

        return select(
            [eastern, northwest, south_central, southwest],
            [
                CTC4KRegion.EASTERN,
                CTC4KRegion.NORTHWEST,
                CTC4KRegion.SOUTH_CENTRAL,
                CTC4KRegion.SOUTHWEST,
            ],
            default=CTC4KRegion.NORTH_CENTRAL,
        )
