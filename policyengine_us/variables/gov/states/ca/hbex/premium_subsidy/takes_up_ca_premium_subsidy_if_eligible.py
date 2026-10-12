from policyengine_us.model_api import *


class takes_up_ca_premium_subsidy_if_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether an eligible tax unit takes up the California Premium Subsidy"
    definition_period = YEAR
    default_value = True
    defined_for = StateCode.CA
