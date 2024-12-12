from policyengine_us.model_api import *


class NorthEastCounty(Enum):
    BOSTON = "Boston"
    NEW_YORK = "New York"
    PHILADELPHIA = "Philadelphia"
    NORTHEAST_DEFAULT = "Northeast default"


class northeast_county(Variable):
    value_type = Enum
    entity = Household
    possible_values = NorthEastCounty
    default_value = NorthEastCounty.NORTHEAST_DEFAULT
    definition_period = YEAR
    defined_for = "is_northeast_region"
    label = "Northeast region county group"

    def formula(household, period, parameters):
        county = household("county_str", period)

        p = parameters(period).household.county_group

        return select(
            [
                np.isin(county, p.northeast.boston),
                np.isin(county, p.northeast.new_york),
                np.isin(county, p.northeast.philadelphia),
            ],
            [
                NorthEastCounty.BOSTON,
                NorthEastCounty.NEW_YORK,
                NorthEastCounty.PHILADELPHIA,
            ],
            default=NorthEastCounty.NORTHEAST_DEFAULT,
        )
