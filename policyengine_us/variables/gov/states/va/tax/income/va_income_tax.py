from policyengine_us.model_api import *


class va_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA
    adds = ["va_income_tax_before_refundable_credits"]
    subtracts = ["va_refundable_credits"]
