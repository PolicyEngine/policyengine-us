from policyengine_us.model_api import *


class ut_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah income tax"
    unit = USD
    definition_period = YEAR
    adds = ["ut_income_tax_before_refundable_credits"]
    defined_for = StateCode.UT
