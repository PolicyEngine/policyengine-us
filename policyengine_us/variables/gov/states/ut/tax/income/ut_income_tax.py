from policyengine_us.model_api import *


class ut_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = (
        "https://tax.utah.gov/forms/current/tc-40.pdf#page=2"  # line 38
    )

    adds = ["ut_income_tax_before_refundable_credits"]
    subtracts = ["ut_refundable_credits"]
