from policyengine_us.model_api import *


class spm_unit_head_spouse_earned_cap(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit lower-earner cap for work and childcare expenses"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        earned_income = person("earned_income", period)
        eligible_earnings = is_head_or_spouse * np.maximum(earned_income, 0)

        count_head_or_spouse = spm_unit.sum(is_head_or_spouse)
        total_earned = spm_unit.sum(eligible_earnings)
        max_earned = spm_unit.max(eligible_earnings)

        return where(count_head_or_spouse > 1, total_earned - max_earned, total_earned)
