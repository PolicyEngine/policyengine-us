from policyengine_us.model_api import *


class sd_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Dakota TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://sdlegislature.gov/Rules/Administrative/67:10:03:05"
    defined_for = StateCode.SD

    adds = ["sd_tanf_countable_earned_income_person"]
