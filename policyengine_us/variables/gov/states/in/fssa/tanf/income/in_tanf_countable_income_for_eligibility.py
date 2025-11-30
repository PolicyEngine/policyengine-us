from policyengine_us.model_api import *


class in_tanf_countable_income_for_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF countable income for eligibility determination"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://iar.iga.in.gov/code/2026/470/10.3#470-10.3-4-4",
        "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-2-3",
    )
    defined_for = StateCode.IN

    adds = [
        "in_tanf_countable_earned_income_for_eligibility",
        "tanf_gross_unearned_income",
    ]
