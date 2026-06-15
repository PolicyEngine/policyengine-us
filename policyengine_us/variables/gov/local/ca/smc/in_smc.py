from policyengine_us.model_api import *


class in_smc(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in San Mateo County"

    def formula(household, period, parameters):
        return household("county_str", period) == "SAN_MATEO_COUNTY_CA"
