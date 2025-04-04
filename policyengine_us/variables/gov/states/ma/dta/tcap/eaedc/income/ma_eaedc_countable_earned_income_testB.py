from policyengine_us.model_api import *


class ma_eaedc_countable_earned_income_testB(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-500"  # (B) step 2

    adds = ["ma_eaedc_earned_income_after_disregard_person"]
