from policyengine_us.model_api import *


class ga_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia income tax after refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
    adds = ["ga_income_tax_before_refundable_credits"]
    subtracts = ["ga_refundable_credits"]
