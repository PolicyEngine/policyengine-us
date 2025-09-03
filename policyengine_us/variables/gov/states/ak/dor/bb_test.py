from policyengine_us.model_api import *


class bb_test(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in Alameda County"

    def formula(household, period, parameters):
        county = household("county_str", period)
        return county == "LA_COUNTY_CA"
