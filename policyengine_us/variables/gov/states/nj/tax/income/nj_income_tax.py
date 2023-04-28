from policyengine_us.model_api import *


class nj_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
    adds = ["nj_income_tax_before_refundable_credits"]
    subtracts = ["nj_refundable_credits"]
