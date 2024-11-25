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
        county = household("county_str", period)

        anchorage_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.west.anchorage

        denver_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.west.denver

        honolulu_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.west.honolulu

        los_angeles_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.west.los_angeles

        phoenix_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.west.phoenix

        san_diego_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.west.san_diego

        san_francisco_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.west.san_francisco

        seattle_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.west.seattle

        return select(
            [
                np.isin(county, anchorage_counties),
                np.isin(county, denver_counties),
                np.isin(county, honolulu_counties),
                np.isin(county, los_angeles_counties),
                np.isin(county, phoenix_counties),
                np.isin(county, san_diego_counties),
                np.isin(county, san_francisco_counties),
                np.isin(county, seattle_counties),
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
