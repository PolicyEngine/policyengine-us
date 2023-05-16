from policyengine_us.model_api import *


class ky_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kenntucky income tax"
    unit = USD
    definition_period = YEAR
    adds = ["ky_income_tax_before_refundable_credits"]
    subtracts = ["ky_refundable_credits"]