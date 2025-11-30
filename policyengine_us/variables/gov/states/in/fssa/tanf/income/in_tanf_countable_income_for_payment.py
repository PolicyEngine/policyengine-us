from policyengine_us.model_api import *


class in_tanf_countable_income_for_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF countable income for payment calculation"
    unit = USD
    definition_period = MONTH
    reference = "https://iar.iga.in.gov/code/2026/470/10.3#470-10.3-4-4"
    defined_for = StateCode.IN

    adds = ["in_tanf_countable_earned_income", "tanf_gross_unearned_income"]
