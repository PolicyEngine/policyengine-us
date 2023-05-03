from policyengine_us.model_api import *


class nj_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
    adds = ["ny_income_tax_before_refundable_credits"]
    subtracts = ["ny_refundable_credits"]
