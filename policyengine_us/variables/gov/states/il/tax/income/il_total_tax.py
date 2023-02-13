from policyengine_us.model_api import *


class il_total_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois total tax"
    unit = USD
    definition_period = YEAR

    defined_for = StateCode.IL

    adds = ["il_income_tax_before_refundable_credits", "il_use_tax"]
