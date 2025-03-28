from policyengine_us.model_api import *


class SouthernCounty(Enum):
    ATLANTA = "Atlanta"
    BALTIMORE = "Baltimore"
    DALLAS_FT_WORTH = "Dallas-Ft. Worth"
    HOUSTON = "Houston"
    MIAMI = "Miami"
    TAMPA = "Tampa"
    WASHINGTON_DC = "Washington DC"
    SOUTH_DEFAULT = "South default"
    NONE = "None"


class southern_county(Variable):
    value_type = Enum
    entity = Household
    possible_values = SouthernCounty
    default_value = SouthernCounty.NONE
    definition_period = YEAR
    defined_for = "is_southern_region"
    label = "Southern region county group"
    reference = "https://www.irs.gov/businesses/small-businesses-self-employed/local-standards-transportation"

    def formula(household, period, parameters):
        county = household("county_str", period)

        p = parameters(period).household.county_group

        atlanta = np.isin(county, p.south.atlanta)
        baltimore = np.isin(county, p.south.baltimore)
        dallas_ft_worth = np.isin(county, p.south.dallas_ft_worth)
        houston = np.isin(county, p.south.houston)
        miami = np.isin(county, p.south.miami)
        tampa = np.isin(county, p.south.tampa)
        washington_dc = np.isin(county, p.south.washington_dc)

        conditions = [
            atlanta,
            baltimore,
            dallas_ft_worth,
            houston,
            miami,
            tampa,
            washington_dc,
            ~(
                atlanta
                | baltimore
                | dallas_ft_worth
                | houston
                | miami
                | tampa
                | washington_dc
            ),
        ]
        results = [
            SouthernCounty.ATLANTA,
            SouthernCounty.BALTIMORE,
            SouthernCounty.DALLAS_FT_WORTH,
            SouthernCounty.HOUSTON,
            SouthernCounty.MIAMI,
            SouthernCounty.TAMPA,
            SouthernCounty.WASHINGTON_DC,
            SouthernCounty.SOUTH_DEFAULT,
        ]

        return select(
            conditions,
            results,
            default=SouthernCounty.NONE,
        )
