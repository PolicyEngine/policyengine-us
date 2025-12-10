from policyengine_us.model_api import *


class ut_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Utah Family Employment Program countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://adminrules.utah.gov/public/rule/R986-200/Current%20Rules"
    )
    defined_for = StateCode.UT

    adds = [
        "ut_tanf_countable_earned_income",
        "tanf_gross_unearned_income",
    ]
