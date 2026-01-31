from policyengine_us.model_api import *


class county_str(Variable):
    value_type = str
    entity = Household
    label = "County (string)"
    documentation = "County variable, stored as a string"
    definition_period = YEAR

    def formula(household, period, parameters):  # pragma: no cover
        return household("county", period).decode_to_str()
