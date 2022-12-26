from policyengine_us.model_api import *


class wa_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WA
    adds = ["wa_income_tax_before_refundable_credits"]
    subtracts = ["wa_refundable_credits"]
