from policyengine_us.model_api import *


class az_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.azleg.gov/ars/46/00292.htm"
    defined_for = StateCode.AZ

    adds = ["az_tanf_countable_earned_income", "tanf_gross_unearned_income"]
