from policyengine_us.model_api import *
import numpy as np


class in_nyc(Variable):
    value_type = bool
    entity = Household
    definition_period = ETERNITY
    label = "Is in NYC"

    def formula(household, period, parameters):
        # Get the county.
        county = household("county_str", period)

        NYC_COUNTIES = [
            "NEW_YORK_COUNTY_NY",
            "KINGS_COUNTY_NY",
            "QUEENS_COUNTY_NY",
            "RICHMOND_COUNTY_NY",
            "BRONX_COUNTY_NY",
        ]
        return np.isin(county, NYC_COUNTIES)
