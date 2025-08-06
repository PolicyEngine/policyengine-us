from policyengine_us.model_api import *


class dc_gac_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC General Assistance for Children (GAC) countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.05a#(e)"
    )
    defined_for = StateCode.DC

    adds = [
        "dc_gac_earned_income_after_disregard_person",
        "dc_gac_countable_unearned_income_person",
    ]
