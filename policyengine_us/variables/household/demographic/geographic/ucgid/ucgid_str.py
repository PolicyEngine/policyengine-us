from policyengine_us.model_api import *


class ucgid_str(Variable):
    value_type = str
    entity = Household
    label = "UCGID (string)"
    documentation = "UCGID variable, stored as a string"
    definition_period = YEAR

    def formula(household, period, parameters):
        return household("ucgid", period).decode_to_str()
