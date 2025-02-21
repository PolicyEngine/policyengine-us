from policyengine_us.model_api import *


class in_la(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in Los Angeles County"

    def formula(household, period, parameters):
        county = household("county_str", period)
        return county == "LOS_ANGELES_COUNTY_CA"
