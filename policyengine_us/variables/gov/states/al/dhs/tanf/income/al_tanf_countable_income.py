from policyengine_us.model_api import *


class al_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama TANF countable income"
    definition_period = MONTH
    reference = "https://dhr.alabama.gov/wp-content/uploads/2022/04/Appendix-N-Sec-2-Public-Assistance-Payment-Manual.pdf#page=37"
    defined_for = StateCode.AL

    adds = ["al_tanf_countable_earned_income", "tanf_gross_unearned_income"]
