from policyengine_us.model_api import *


class or_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR income tax after refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR
    adds = ["or_income_tax_before_refundable_credits"]
    subtracts = ["or_refundable_credits"]
