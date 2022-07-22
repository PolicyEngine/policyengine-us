from openfisca_us.model_api import *


class state_code_str(Variable):
    value_type = str
    entity = Household
    label = "State code (string)"
    documentation = "State code variable, stored as a string"
    definition_period = YEAR

    def formula(household, period, parameters):
        return household("state_code", period).decode_to_str()
