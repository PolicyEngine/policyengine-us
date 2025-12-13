from policyengine_us.model_api import *


class wi_works_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wisconsin Works countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/03.2.7_Counting_Income.htm",
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/03.2.8_DISREGARDING_INCOME.htm",
    )
    defined_for = StateCode.WI
    # Wisconsin disregards child support, which is included in
    # tanf_gross_unearned_income. The result cannot be negative.
    adds = ["tanf_gross_earned_income", "tanf_gross_unearned_income"]
    subtracts = ["child_support_received"]
