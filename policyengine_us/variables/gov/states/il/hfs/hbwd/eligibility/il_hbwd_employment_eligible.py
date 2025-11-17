from policyengine_us.model_api import *


class il_hbwd_employment_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities employment eligible"
    definition_period = MONTH
    reference = (
        "https://ilga.gov/commission/jcar/admincode/089/089001200I05100R.html",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Must be employed or self-employed with earned income
        earned_income = person("il_hbwd_gross_earned_income", period)
        return earned_income > 0
