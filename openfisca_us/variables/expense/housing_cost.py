from openfisca_us.model_api import *


class housing_cost(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing cost"
    documentation = "Housing cost for this SPM unit"
    unit = USD
    definition_period = YEAR
