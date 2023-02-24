from policyengine_us.model_api import *


class in_nyc(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in NYC"
    # Currently disabled to allow entry until we collect county.
    # County of the below list.
    # NYC_COUNTIES = [
    #   "NEW_YORK_COUNTY_NY",
    #   "KINGS_COUNTY_NY",
    #   "QUEENS_COUNTY_NY",
    #   "RICHMOND_COUNTY_NY",
    #   "BRONX_COUNTY_NY",
    # ]
