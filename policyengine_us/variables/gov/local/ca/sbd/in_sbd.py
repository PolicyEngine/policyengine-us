from policyengine_us.model_api import *


class in_sbd(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in San Bernardino County"

    def formula(household, period, parameters):
        county = household("county_str", period)
        return county == "SAN_BERNARDINO_COUNTY_CA"
