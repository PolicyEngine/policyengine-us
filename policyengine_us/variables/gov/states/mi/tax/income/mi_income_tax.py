from policyengine_us.model_api import *


class mi_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI

    adds = ["mi_income_tax_before_refundable_credits"]
    subtracts = ["mi_refundable_credits"]
