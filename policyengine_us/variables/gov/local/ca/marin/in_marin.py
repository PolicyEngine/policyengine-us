from policyengine_us.model_api import *


class in_marin(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in Marin County"

    def formula(household, period, parameters):
        county = household("county_str", period)
        return county == "MARIN_COUNTY_CA"
