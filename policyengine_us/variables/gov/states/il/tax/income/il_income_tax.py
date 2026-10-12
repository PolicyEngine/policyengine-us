from policyengine_us.model_api import *


class il_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL

    adds = ["il_income_tax_before_refundable_credits"]
    subtracts = ["il_refundable_credits"]
