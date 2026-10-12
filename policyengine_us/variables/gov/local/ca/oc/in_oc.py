from policyengine_us.model_api import *


class in_oc(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in Orange County"

    def formula(household, period, parameters):
        county = household("county_str", period)
        return county == "ORANGE_COUNTY_CA"
