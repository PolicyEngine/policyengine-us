from policyengine_us.model_api import *


class in_san_francisco(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in San Francisco County"

    def formula(household, period, parameters):
        county = household("county_str", period)
        return county == "SAN_FRANCISCO_COUNTY_CA"
