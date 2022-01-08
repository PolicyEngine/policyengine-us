from openfisca_us.model_api import *


class state_group_str(Variable):
    value_type = str
    entity = Household
    label = "State group (string)"
    documentation = "State group variable, stored as a string"
    definition_period = YEAR

    def formula(household, period, parameters):
        return household("state_group", period).decode_to_str()
