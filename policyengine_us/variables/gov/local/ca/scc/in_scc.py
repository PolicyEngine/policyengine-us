from policyengine_us.model_api import *


class in_scc(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in Santa Clara County"

    def formula(household, period, parameters):
        county = household("county_str", period)
        return county == "SANTA_CLARA_COUNTY_CA"
