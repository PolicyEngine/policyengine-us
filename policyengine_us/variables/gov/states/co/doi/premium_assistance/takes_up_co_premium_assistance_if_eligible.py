from policyengine_us.model_api import *


class takes_up_co_premium_assistance_if_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether an eligible tax unit takes up Colorado Premium Assistance"
    definition_period = YEAR
    defined_for = StateCode.CO
    default_value = True
