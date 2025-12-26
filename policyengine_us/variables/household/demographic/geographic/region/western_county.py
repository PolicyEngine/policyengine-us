from policyengine_us.model_api import *


class WesternCounty(Enum):
    ANCHORAGE = "Anchorage"
    DENVER = "Denver"
    HONOLULU = "Honolulu"
    LOS_ANGELES = "Los Angeles"
    PHOENIX = "Phoenix"
    SAN_DIEGO = "San Diego"
    SAN_FRANCISCO = "San Francisco"
    SEATTLE = "Seattle"
    WEST_DEFAULT = "West default"
    NONE = "None"


class western_county(Variable):
    value_type = Enum
    entity = Household
    possible_values = WesternCounty
    default_value = WesternCounty.NONE
    definition_period = YEAR
    defined_for = "is_western_region"
    label = "Western region county group"
    reference = "https://www.irs.gov/businesses/small-businesses-self-employed/local-standards-transportation"

    def formula(household, period, parameters):
        county = household("county", period).decode_to_str()

        p = parameters(period).household.county_group

        anchorage = np.isin(county, p.west.anchorage)
        denver = np.isin(county, p.west.denver)
        honolulu = np.isin(county, p.west.honolulu)
        los_angeles = np.isin(county, p.west.los_angeles)
        phoenix = np.isin(county, p.west.phoenix)
        san_diego = np.isin(county, p.west.san_diego)
        san_francisco = np.isin(county, p.west.san_francisco)
        seattle = np.isin(county, p.west.seattle)

        conditions = [
            anchorage,
            denver,
            honolulu,
            los_angeles,
            phoenix,
            san_diego,
            san_francisco,
            seattle,
            ~(
                anchorage
                | denver
                | honolulu
                | los_angeles
                | phoenix
                | san_diego
                | san_francisco
                | seattle
            ),
        ]
        results = [
            WesternCounty.ANCHORAGE,
            WesternCounty.DENVER,
            WesternCounty.HONOLULU,
            WesternCounty.LOS_ANGELES,
            WesternCounty.PHOENIX,
            WesternCounty.SAN_DIEGO,
            WesternCounty.SAN_FRANCISCO,
            WesternCounty.SEATTLE,
            WesternCounty.WEST_DEFAULT,
        ]

        return select(
            conditions,
            results,
            default=WesternCounty.NONE,
        )
