from policyengine_us.model_api import *


class vt_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT
    adds = ["vt_income_tax_before_refundable_credits"]
    subtracts = ["vt_refundable_credits"]
