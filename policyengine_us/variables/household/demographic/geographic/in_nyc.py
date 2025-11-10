from policyengine_us.model_api import *


class in_nyc(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in NYC"

    def formula(household, period, parameters):
        county = household("county_str", period)
        possible_counties = [
            "QUEENS_COUNTY_NY",
            "BRONX_COUNTY_NY",
            "RICHMOND_COUNTY_NY",
            "NEW_YORK_COUNTY_NY",
            "KINGS_COUNTY_NY",
        ]

        return np.isin(county, possible_counties)
