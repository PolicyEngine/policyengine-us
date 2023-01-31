from policyengine_us.model_api import *


class il_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL

    adds = ["il_total_tax"]
    subtracts = ["il_total_payments_and_refundable_credits"]
