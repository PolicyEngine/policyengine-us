from policyengine_us.model_api import *


class in_nyc(Variable):
    value_type = bool
    entity = Household
    definition_period = ETERNITY
    label = "Is in NYC"

    def formula(household, period, parameters):

        # Get the county.
        county = household("county_str", period)

        return county.isin([ 
            "NEW_YORK_COUNTY_NY",
            "KINGS_COUNTY_NY",
            "QUEENS_COUNTY_NY",
            "RICHMOND_COUNTY_NY",
            "BRONX_COUNTY_NY"
        ])
