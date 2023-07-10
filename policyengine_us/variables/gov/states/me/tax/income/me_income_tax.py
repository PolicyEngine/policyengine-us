from policyengine_us.model_api import *


class me_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME
    adds = ["me_income_tax_before_refundable_credits"]
    subtracts = ["me_refundable_credits"]
