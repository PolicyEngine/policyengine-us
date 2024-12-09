from policyengine_us.model_api import *


class WestCounty(Enum):
    ANCHORAGE = "Anchorage"
    DENVER = "Denver"
    HONOLULU = "Honolulu"
    LOS_ANGELES = "Los Angeles"
    PHOENIX = "Phoenix"
    SAN_DIEGO = "San Diego"
    SAN_FRANCISCO = "San Francisco"
    SEATTLE = "Seattle"
    WEST_DEFAULT = "West default"


class west_county(Variable):
    value_type = Enum
    entity = Household
    possible_values = WestCounty
    default_value = WestCounty.WEST_DEFAULT
    definition_period = YEAR
    defined_for = "is_west_region"
    label = "West region state group"

    def formula(household, period, parameters):
        county = household("county", period).decode_to_str()

        p = parameters(
            period
        ).household.county_group

        return select(
            [
                np.isin(county, p.west.anchorage),
                np.isin(county, p.west.denver),
                np.isin(county, p.west.honolulu),
                np.isin(county, p.west.los_angeles),
                np.isin(county, p.west.phoenix),
                np.isin(county, p.west.san_diego),
                np.isin(county, p.west.san_francisco),
                np.isin(county, p.west.seattle),
            ],
            [
                WestCounty.ANCHORAGE,
                WestCounty.DENVER,
                WestCounty.HONOLULU,
                WestCounty.LOS_ANGELES,
                WestCounty.PHOENIX,
                WestCounty.SAN_DIEGO,
                WestCounty.SAN_FRANCISCO,
                WestCounty.SEATTLE,
            ],
            default=WestCounty.WEST_DEFAULT,
        )
