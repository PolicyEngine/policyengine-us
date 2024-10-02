from policyengine_us.model_api import *


class wv_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV
    adds = ["wv_income_tax_before_refundable_credits"]
    subtracts = ["wv_refundable_credits"]
