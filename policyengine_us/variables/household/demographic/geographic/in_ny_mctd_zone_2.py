from policyengine_us.model_api import *


class in_ny_mctd_zone_2(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in New York MCTD Zone 2"

    def formula(household, period, parameters):
        county = household("county_str", period)
        possible_counties = [
            "ROCKLAND_COUNTY_NY",
            "NASSAU_COUNTY_NY",
            "SUFFOLK_COUNTY_NY",
            "ORANGE_COUNTY_NY",
            "PUTNAM_COUNTY_NY",
            "DUTCHESS_COUNTY_NY",
            "WESTCHESTER_COUNTY_NY",
        ]

        return np.isin(county, possible_counties)
