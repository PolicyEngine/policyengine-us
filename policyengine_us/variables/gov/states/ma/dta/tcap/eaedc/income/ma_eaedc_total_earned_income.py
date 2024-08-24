from policyengine_us.model_api import *


class ma_eaedc_total_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC total earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA

    adds = ["ma_eaedc_earned_income"]
    subtracts = ["ma_eaedc_disabled_earned_income"]
