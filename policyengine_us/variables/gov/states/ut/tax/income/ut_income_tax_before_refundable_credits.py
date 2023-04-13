from policyengine_us.model_api import *


class ut_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    adds = ["ut_income_tax_before_credits"]
    defined_for = StateCode.UT
