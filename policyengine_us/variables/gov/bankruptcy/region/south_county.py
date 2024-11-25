from policyengine_us.model_api import *


class SouthCounty(Enum):
    ATLANTA = "Atlanta"
    BALTIMORE = "Baltimore"
    DALLAS_FT_WORTH = "Dallas-Ft. Worth"
    HOUSTON = "Houston"
    MIAMI = "Miami"
    TAMPA = "Tampa"
    WASHINGTON_DC = "Washington DC"
    SOUTH_DEFAULT = "South default"


class south_county(Variable):
    value_type = Enum
    entity = Household
    possible_values = SouthCounty
    default_value = SouthCounty.SOUTH_DEFAULT
    definition_period = YEAR
    defined_for = "is_south_region"
    label = "South region state group"

    def formula(household, period, parameters):
        county = household("county_str", period)

        atlanta_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.south.atlanta

        baltimore_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.south.baltimore

        dallas_ft_worth_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.south.dallas_ft_worth

        houston_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.south.houston

        miami_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.south.miami

        tampa_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.south.tampa

        washington_dc_counties = parameters(
            period
        ).gov.bankruptcy.local_standards.vehicle_operation.region_group.south.washington_dc

        return select(
            [
                np.isin(county, atlanta_counties),
                np.isin(county, baltimore_counties),
                np.isin(county, dallas_ft_worth_counties),
                np.isin(county, houston_counties),
                np.isin(county, miami_counties),
                np.isin(county, tampa_counties),
                np.isin(county, washington_dc_counties),
            ],
            [
                SouthCounty.ATLANTA,
                SouthCounty.BALTIMORE,
                SouthCounty.DALLAS_FT_WORTH,
                SouthCounty.HOUSTON,
                SouthCounty.MIAMI,
                SouthCounty.TAMPA,
                SouthCounty.WASHINGTON_DC,
            ],
            default=SouthCounty.SOUTH_DEFAULT,
        )
