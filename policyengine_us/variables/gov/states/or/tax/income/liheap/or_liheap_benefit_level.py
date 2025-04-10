from policyengine_us.model_api import *


class or_liheap_benefit_level(Variable):
    value_type = int
    entity = SPMUnit
    label = "Income range for Oregon LIHEAP eligibility"
    definition_period = YEAR
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2021-Energy-Assistance-Manual.pdf#page=55"

    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["irs_gross_income"])
        threshold = spm_unit("or_liheap_income_threshold", period)
        p = parameters(period).gov.states["or"].mder.liheap

        level_one = threshold * p.or_liheap_benefit_level_multiplier
        level_two = threshold * p.or_liheap_benefit_level_multiplier * 2
        level_three = threshold * p.or_liheap_benefit_level_multiplier * 3

        return select(
            [
                income <= level_one,
                income <= level_two,
                income <= level_three,
            ],
            [
                1,
                2,
                3,
            ],
            default=4,
        )
