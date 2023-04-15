from policyengine_us.model_api import *


class ut_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah income tax"
    unit = USD
    definition_period = YEAR
    adds = ["ut_income_tax_before_credits"]
    subtracts = [
        "ut_taxpayer_credit",
        "ut_eitc",
        "ut_retirement_credit",
        "ut_ss_benefits_credit",
    ]
    defined_for = StateCode.UT
