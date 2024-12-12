from policyengine_us.model_api import *


class MidWestCounty(Enum):
    CHICAGO = "Chicago"
    CLEVELAND = "Cleveland"
    DETROIT = "Detroit"
    MINNEAPOLIS_ST_PAUL = "Minneapolis-St. Paul"
    ST_LOUIS = "St. Louis"
    MIDWEST_DEFAULT = "Midwest default"


class midwest_county(Variable):
    value_type = Enum
    entity = Household
    possible_values = MidWestCounty
    default_value = MidWestCounty.MIDWEST_DEFAULT
    definition_period = YEAR
    defined_for = "is_midwest_region"
    label = "Midwest region county group"

    def formula(household, period, parameters):
        county = household("county_str", period)

        p = parameters(period).household.county_group

        return select(
            [
                np.isin(county, p.midwest.chicago),
                np.isin(county, p.midwest.cleveland),
                np.isin(county, p.midwest.detroit),
                np.isin(county, p.midwest.minneapolis_st_paul),
                np.isin(county, p.midwest.st_louis),
            ],
            [
                MidWestCounty.CHICAGO,
                MidWestCounty.CLEVELAND,
                MidWestCounty.DETROIT,
                MidWestCounty.MINNEAPOLIS_ST_PAUL,
                MidWestCounty.ST_LOUIS,
            ],
            default=MidWestCounty.MIDWEST_DEFAULT,
        )
