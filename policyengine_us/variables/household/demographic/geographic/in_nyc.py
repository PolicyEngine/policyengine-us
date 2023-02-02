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
        # counties = county.possible_values

        # Return whether the county is NYC.
        # return county in [
        #     counties.NEW_YORK_COUNTY_NY,
        #     counties.KINGS_COUNTY_NY,
        #     counties.QUEENS_COUNTY_NY,
        #     counties.RICHMOND_COUNTY_NY,
        #     counties.BRONX_COUNTY_NY,
        # ]

        # Like this or is there a way to do it with County.NEW_YORK_COUNTY_NY.county_str?
        return county in [ 
            "NEW_YORK_COUNTY_NY",
            "KINGS_COUNTY_NY",
            "QUEENS_COUNTY_NY",
            "RICHMOND_COUNTY_NY",
            "BRONX_COUNTY_NY"
        ]
