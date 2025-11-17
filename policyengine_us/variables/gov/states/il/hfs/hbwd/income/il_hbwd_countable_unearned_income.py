from policyengine_us.model_api import *


class il_hbwd_countable_unearned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities countable unearned income"
    definition_period = MONTH
    reference = (
        "https://ilga.gov/commission/jcar/admincode/089/089001200I03300R.html",
        "https://ilga.gov/commission/jcar/admincode/089/089001200I05100R.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Unearned income is counted without deductions for HBWD
        return person("il_hbwd_gross_unearned_income", period)
