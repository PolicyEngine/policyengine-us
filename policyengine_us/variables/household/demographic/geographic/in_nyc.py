from policyengine_us.model_api import *


class in_nyc(Variable):
    value_type = bool
    entity = Household
    definition_period = ETERNITY
    label = "Is in NYC"

    def formula(household, period, parameters):

        # Get the county.
        county = household("county_str", period)

        # Get possible counties.
        counties = county.possible_values

        # Return whether the county is NYC.
        return county in [
            counties.NEW_YORK_COUNTY_NY,
            counties.KINGS_COUNTY_NY,
            counties.QUEENS_COUNTY_NY,
            counties.RICHMOND_COUNTY_NY,
            counties.BRONX_COUNTY_NY
        ]

