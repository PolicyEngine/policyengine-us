from policyengine_us.model_api import *


class in_harris_county_tx(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in Harris County, Texas"

    def formula(household, period, parameters):
        county = household("county_str", period)
        return county == "HARRIS_COUNTY_TX"
