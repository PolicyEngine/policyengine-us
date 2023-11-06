from policyengine_us.model_api import *


class la_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana income tax"
    defined_for = StateCode.LA
    unit = USD
    definition_period = YEAR

    adds = ["la_income_tax_before_refundable_credits"]
    subtracts = ["la_refundable_credits"]
