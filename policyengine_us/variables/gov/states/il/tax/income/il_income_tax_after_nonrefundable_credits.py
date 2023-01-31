from policyengine_us.model_api import *


class il_income_tax_after_nonrefundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL income tax after nonrefundable credits"
    unit = USD
    definition_period = YEAR

    defined_for = StateCode.IL

    adds = ["il_income_tax_before_nonrefundable_credits"]
    subtracts = ["il_nonrefundable_credits"]
