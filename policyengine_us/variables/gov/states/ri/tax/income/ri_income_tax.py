from policyengine_us.model_api import *


class ri_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island income tax"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR
    adds = ["ri_income_tax_before_refundable_credits"]
    subtracts = ["ri_refundable_credits"]
