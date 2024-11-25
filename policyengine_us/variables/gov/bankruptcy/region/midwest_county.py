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
    label = "Midwest region state group"

    def formula(household, period, parameters):
        county = household("county_str", period)

        chicago_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.midwest.chicago

        cleveland_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.midwest.cleveland

        detroit_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.midwest.detroit

        minneapolis_st_paul_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.midwest.minneapolis_st_paul

        st_louis_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.midwest.st_louis

        return select(
            [
                np.isin(county, chicago_counties),
                np.isin(county, cleveland_counties),
                np.isin(county, detroit_counties),
                np.isin(county, minneapolis_st_paul_counties),
                np.isin(county, st_louis_counties),
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
