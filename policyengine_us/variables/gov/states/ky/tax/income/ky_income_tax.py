from policyengine_us.model_api import *


class ky_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    adds = ["ky_income_tax_before_refundable_credits"]
    subtracts = ["ky_refundable_credits"]
