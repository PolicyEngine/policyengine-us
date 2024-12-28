from policyengine_us.model_api import *


class MidWesternCounty(Enum):
    CHICAGO = "Chicago"
    CLEVELAND = "Cleveland"
    DETROIT = "Detroit"
    MINNEAPOLIS_ST_PAUL = "Minneapolis-St. Paul"
    ST_LOUIS = "St. Louis"
    MIDWEST_DEFAULT = "Midwest default"
    NONE = "None"


class midwestern_county(Variable):
    value_type = Enum
    entity = Household
    possible_values = MidWesternCounty
    default_value = MidWesternCounty.NONE
    definition_period = YEAR
    defined_for = "is_midwestern_region"
    label = "Midwestern region county group"
    reference = "https://www.irs.gov/businesses/small-businesses-self-employed/local-standards-transportation"

    def formula(household, period, parameters):
        county = household("county_str", period)

        p = parameters(period).household.county_group

        chicago = np.isin(county, p.midwest.chicago)
        cleveland = np.isin(county, p.midwest.cleveland)
        detroit = np.isin(county, p.midwest.detroit)
        minneapolis_st_paul = np.isin(county, p.midwest.minneapolis_st_paul)
        st_louis = np.isin(county, p.midwest.st_louis)

        conditions = [
            chicago,
            cleveland,
            detroit,
            minneapolis_st_paul,
            st_louis,
            ~(chicago | cleveland | detroit | minneapolis_st_paul | st_louis),
        ]
        results = [
            MidWesternCounty.CHICAGO,
            MidWesternCounty.CLEVELAND,
            MidWesternCounty.DETROIT,
            MidWesternCounty.MINNEAPOLIS_ST_PAUL,
            MidWesternCounty.ST_LOUIS,
            MidWesternCounty.MIDWEST_DEFAULT,
        ]

        return select(
            conditions,
            results,
            default=MidWesternCounty.NONE,
        )
