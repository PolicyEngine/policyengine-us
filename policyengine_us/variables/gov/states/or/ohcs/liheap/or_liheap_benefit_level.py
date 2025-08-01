from policyengine_us.model_api import *


class or_liheap_benefit_level(Variable):
    value_type = int
    entity = SPMUnit
    label = "Income level for Oregon LIHEAP payment"
    definition_period = YEAR
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2021-Energy-Assistance-Manual.pdf#page=55"
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["irs_gross_income"])
        threshold = spm_unit("or_liheap_income_threshold", period)
        p = parameters(period).gov.states["or"].ohcs.liheap

        levels = [
            threshold * p.benefit_level_multiplier * i
            for i in range(1, 4)
        ]

        return select(
            [income <= level for level in levels],
            list(range(1, 4)),
            default=4,
        )
