from openfisca_us.model_api import *


class phone_cost(Variable):
    value_type = float
    entity = SPMUnit
    label = "Phone cost"
    documentation = "Phone line cost for this SPM unit"
    unit = USD
    definition_period = YEAR
