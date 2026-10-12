from policyengine_us.model_api import *


class in_tanf_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF gross income"
    unit = USD
    definition_period = MONTH
    reference = "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-1-1.7"
    defined_for = StateCode.IN

    adds = ["tanf_gross_earned_income", "tanf_gross_unearned_income"]
