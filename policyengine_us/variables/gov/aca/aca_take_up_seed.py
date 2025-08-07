from policyengine_us.model_api import *


class aca_take_up_seed(Variable):
    value_type = float
    entity = TaxUnit
    label = "Randomly assigned seed for ACA take-up"
    definition_period = YEAR
