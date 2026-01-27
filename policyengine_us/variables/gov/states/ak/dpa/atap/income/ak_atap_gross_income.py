from policyengine_us.model_api import *


class ak_atap_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP gross income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.470"
    defined_for = StateCode.AK

    adds = ["tanf_gross_earned_income", "tanf_gross_unearned_income"]
