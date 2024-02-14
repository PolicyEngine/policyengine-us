from policyengine_us.model_api import *


class al_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AL

    adds = ["al_income_tax_before_refundable_credits"]
    subtracts = ["al_refundable_credits"]
