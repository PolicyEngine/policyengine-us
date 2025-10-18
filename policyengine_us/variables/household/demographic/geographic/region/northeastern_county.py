from policyengine_us.model_api import *


class NorthEasternCounty(Enum):
    BOSTON = "Boston"
    NEW_YORK = "New York"
    PHILADELPHIA = "Philadelphia"
    NORTHEAST_DEFAULT = "Northeast default"
    NONE = "None"


class northeastern_county(Variable):
    value_type = Enum
    entity = Household
    possible_values = NorthEasternCounty
    default_value = NorthEasternCounty.NONE
    definition_period = YEAR
    defined_for = "is_northeastern_region"
    label = "Northeastern region county group"
    reference = "https://www.irs.gov/businesses/small-businesses-self-employed/local-standards-transportation"

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
            NorthEasternCounty.BOSTON,
            NorthEasternCounty.NEW_YORK,
            NorthEasternCounty.PHILADELPHIA,
            NorthEasternCounty.NORTHEAST_DEFAULT,
        ]

        return select(
            conditions,
            results,
            default=NorthEasternCounty.NONE,
        )
