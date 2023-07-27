from policyengine_us.model_api import *


class co_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    adds = ["co_income_tax_before_refundable_credits"]
    subtracts = ["co_refundable_credits"]
