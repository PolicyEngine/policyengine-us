from policyengine_us.model_api import *


class hi_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    adds = ["hi_income_tax_before_refundable_credits"]
    subtracts = ["hi_refundable_credits"]
