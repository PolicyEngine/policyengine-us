from policyengine_us.model_api import *


class in_riv(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in Riverside County"

    def formula(household, period, parameters):
        county = household("county_str", period)
        return county == "RIVERSIDE_COUNTY_CA"
