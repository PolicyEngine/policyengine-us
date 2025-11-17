from policyengine_us.model_api import *


class il_hbwd_countable_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities countable income"
    definition_period = MONTH
    reference = (
        "https://ilga.gov/commission/jcar/admincode/089/089001200I05100R.html",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
    )
    defined_for = StateCode.IL

    adds = [
        "il_hbwd_countable_earned_income",
        "il_hbwd_countable_unearned_income",
    ]
