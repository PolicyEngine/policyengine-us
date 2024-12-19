from policyengine_us.model_api import *


class NorthEastCounty(Enum):
    BOSTON = "Boston"
    NEW_YORK = "New York"
    PHILADELPHIA = "Philadelphia"
    NORTHEAST_DEFAULT = "Northeast default"
    NONE = "None"


class northeast_county(Variable):
    value_type = Enum
    entity = Household
    possible_values = NorthEastCounty
    default_value = NorthEastCounty.NONE
    definition_period = YEAR
    defined_for = "is_northeast_region"
    label = "Northeast region county group"

    def formula(household, period, parameters):
        county = household("county_str", period)

        p = parameters(period).household.county_group
        boston = np.isin(county, p.northeast.boston)
        new_york = np.isin(county, p.northeast.new_york)
        philadelphia = np.isin(county, p.northeast.philadelphia)

        conditions = [
            boston,
            new_york,
            philadelphia,
            ~(boston | new_york | philadelphia),
        ]
        results = [
            NorthEastCounty.BOSTON,
            NorthEastCounty.NEW_YORK,
            NorthEastCounty.PHILADELPHIA,
            NorthEastCounty.NORTHEAST_DEFAULT,
        ]

        return select(
            conditions,
            results,
            default=NorthEastCounty.NONE,
        )
