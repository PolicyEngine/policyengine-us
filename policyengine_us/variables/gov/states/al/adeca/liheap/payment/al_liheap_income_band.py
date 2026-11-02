from policyengine_us.model_api import *


class al_liheap_income_band(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Alabama LIHEAP monthly income band"
    defined_for = StateCode.AL
    reference = "https://liheapch.acf.gov/docs/2026/state-plans/AL_Plan_2026.pdf#page=9"

    def formula(spm_unit, period, parameters):
        monthly_limit = spm_unit("al_liheap_income_limit", period) / MONTHS_IN_YEAR
        monthly_income = spm_unit("al_liheap_countable_income", period) / MONTHS_IN_YEAR
        first_upper = np.floor(monthly_limit / 3 + 0.5)
        second_upper = 2 * first_upper + 1
        # Published upper bounds are inclusive. Fractional dollars immediately
        # above an upper bound enter the next band without a one-dollar gap.
        return select(
            [monthly_income <= first_upper, monthly_income <= second_upper],
            [1, 2],
            default=3,
        )
