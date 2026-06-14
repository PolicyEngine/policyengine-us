from policyengine_us.model_api import *


class in_cc(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in Contra Costa County"

    def formula(household, period, parameters):
        county = household("county_str", period)
        return county == "CONTRA_COSTA_COUNTY_CA"
