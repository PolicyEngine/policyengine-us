from policyengine_us.model_api import *


class or_liheap_income_range(Variable):
    value_type = int
    entity = SPMUnit
    label = "Income range for Oregon LIHEAP eligibility"
    definition_period = YEAR
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2021-Energy-Assistance-Manual.pdf#page=55"

    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        income = spm_unit("adjusted_gross_income", period)
        threshold = spm_unit("or_liheap_income_threshold", period)
        p = parameters(period).gov.states["or"].liheap.income_range

        range1_upper = threshold * p.range1_upper
        range2_upper = threshold * p.range2_upper
        range3_upper = threshold * p.range3_upper

        return select(
            [
                income <= range1_upper,
                income <= range2_upper,
                income <= range3_upper,
            ],
            [1, 2, 3],
            default=4
        )

    