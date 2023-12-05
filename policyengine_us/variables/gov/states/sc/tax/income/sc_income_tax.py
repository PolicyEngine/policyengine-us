from policyengine_us.model_api import *


class sc_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC

    adds = ["sc_income_tax_before_refundable_credits"]
    subtracts = ["sc_refundable_credits"]
