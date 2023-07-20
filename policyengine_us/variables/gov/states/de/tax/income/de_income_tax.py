from policyengine_us.model_api import *


class de_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware personal income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
    adds = ["de_income_tax_before_refundable_credits"]
    subtracts = ["de_refundable_credits"]
