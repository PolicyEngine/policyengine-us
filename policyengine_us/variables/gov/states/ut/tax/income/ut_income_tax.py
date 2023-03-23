from policyengine_us.model_api import *


class ut_income_tax(Variable):
    """
    Line 40 of Utah 2022 Individual Income Tax return form TC-40.
    """

    value_type = float
    entity = TaxUnit
    label = "UT income tax after refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
    adds = ["ut_income_tax_before_refundable_credits"]
    subtracts = ["ut_refundable_credits"]
