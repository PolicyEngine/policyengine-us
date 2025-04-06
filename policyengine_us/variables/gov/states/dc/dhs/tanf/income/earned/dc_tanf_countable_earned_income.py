from policyengine_us.model_api import *


class dc_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC Temporary Assistance for Needy Families (TANF) countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.11"
    )

    adds = ["dc_tanf_earned_income_after_disregard_person"]
