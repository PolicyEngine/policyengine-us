from openfisca_us.model_api import *


class phone_cost(Variable):
    value_type = float
    entity = SPMUnit
    label = "Phone cost"
    unit = USD
    definition_period = YEAR
