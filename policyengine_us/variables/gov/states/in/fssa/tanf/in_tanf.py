from policyengine_us.model_api import *


class in_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-2-5",
        "https://iar.iga.in.gov/code/2026/470/10.3#470-10.3-4-4",
    )
    defined_for = "in_tanf_eligible"

    def formula(spm_unit, period, parameters):
        maximum_benefit = spm_unit("in_tanf_maximum_benefit", period)
        countable_income = spm_unit("in_tanf_countable_income_for_payment", period)
        benefit = max_(maximum_benefit - countable_income, 0)
        # Cap at the maximum benefit so negative countable income cannot
        # inflate the grant above the maximum.
        return min_(benefit, maximum_benefit)
