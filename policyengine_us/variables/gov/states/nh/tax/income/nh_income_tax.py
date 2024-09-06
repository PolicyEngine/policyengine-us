from policyengine_us.model_api import *


class nh_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH
    adds = ["nh_income_tax_before_refundable_credits"]
    subtracts = ["nh_refundable_credits"]
