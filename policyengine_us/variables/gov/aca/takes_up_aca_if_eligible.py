from policyengine_us.model_api import *


class takes_up_aca_if_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether an eligible tax unit takes up ACA"
    definition_period = YEAR
    default_value = True
