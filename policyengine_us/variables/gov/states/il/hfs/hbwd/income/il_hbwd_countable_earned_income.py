from policyengine_us.model_api import *


class il_hbwd_countable_earned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities countable earned income"
    definition_period = MONTH
    reference = (
        "https://ilga.gov/commission/jcar/admincode/089/089001200I03600R.html",
        "https://ilga.gov/commission/jcar/admincode/089/089001200I05100R.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        gross_earned = person("il_hbwd_gross_earned_income", period)
        deductions = person("il_hbwd_income_deductions", period)
        return max_(0, gross_earned - deductions)
