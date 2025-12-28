from policyengine_us.model_api import *


class ar_tea_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arkansas TEA countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    defined_for = StateCode.AR

    adds = ["ar_tea_countable_earned_income", "tanf_gross_unearned_income"]
