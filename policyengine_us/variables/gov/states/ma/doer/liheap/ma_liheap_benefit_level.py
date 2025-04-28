from policyengine_us.model_api import *


class ma_liheap_benefit_level(Variable):
    value_type = int
    entity = SPMUnit
    label = "Benefit Levels for Massachusetts LIHEAP payout"
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-and-benefit-chart-january-2025/download"

    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["irs_gross_income"])
        threshold = spm_unit("ma_liheap_income_threshold", period)
        fpg = spm_unit("spm_unit_fpg", period)
        p = parameters(period).gov.states.ma.doer.liheap

        level_one = fpg
        level_two = fpg * p.benefit_level_multiplier * 5
        level_three = fpg * p.benefit_level_multiplier * 6
        level_four = fpg * p.benefit_level_multiplier * 7
        level_five = fpg * p.benefit_level_multiplier * 8
        level_six = threshold
        return select(
            [
                income <= level_one,
                income <= level_two,
                income <= level_three,
                income <= level_four,
                income <= level_five,
                income <= level_six,
            ],
            [
                1,
                2,
                3,
                4,
                5,
                6,
            ],
            default=6,
        )
