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
    label = "Northeast region state group"

    def formula(household, period, parameters):
        county = household("county_str", period)

        boston_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.northeast.boston

        new_york_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.northeast.new_york

        philadelphia_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.northeast.philadelphia

        return select(
            [
                np.isin(county, boston_counties),
                np.isin(county, new_york_counties),
                np.isin(county, philadelphia_counties),
            ],
            [
                NorthEastCounty.BOSTON,
                NorthEastCounty.NEW_YORK,
                NorthEastCounty.PHILADELPHIA,
            ],
            default=NorthEastCounty.NORTHEAST_DEFAULT,
        )
