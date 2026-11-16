from policyengine_us.model_api import *


class ny_heap_tier_one(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP Tier I status"
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/policy/directives/2016/LCM/16-LCM-16-Attachment-1.pdf#page=1",
        "https://liheapch.acf.gov/docs/NY_BenefitMatrix_2022.pdf#page=1",
        "https://liheapch.acf.gov/docs/NY_Plan_2017.pdf#page=9",
        "https://liheapch.acf.gov/docs/2026/state-plans/NY_Plan_2026.pdf#page=10",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/NY_BenefitMatrix_2026.docx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.otda.heap.payment
        threshold = (
            np.floor(
                # Keep an exact monthly dollar from falling below the integer
                # before floor: float32 can turn 11,880 * 1.3 / 12 into 1,286.9999.
                spm_unit("ny_heap_fpg", period).astype(np.float64)
                * p.tier_one_fpg_rate
                / MONTHS_IN_YEAR
            )
            * MONTHS_IN_YEAR
        )
        return spm_unit("ny_heap_categorically_eligible", period) | (
            spm_unit("ny_heap_countable_income", period) <= threshold
        )

    def formula_2017_01_01(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ny.otda.heap.eligibility.historical_income_limits
        size = max_(spm_unit("ny_heap_household_size", period), 1)
        last_size = p.last_published_household_size
        threshold = p.tier_one.calc(min_(size, last_size)) * MONTHS_IN_YEAR
        table_tier_one = spm_unit("ny_heap_categorically_eligible", period) | (
            spm_unit("ny_heap_countable_income", period) <= threshold
        )
        generic_tier_one = ny_heap_tier_one.formula(spm_unit, period, parameters)
        return where(size <= last_size, table_tier_one, generic_tier_one)

    def formula_2024_01_01(spm_unit, period, parameters):
        return ny_heap_tier_one.formula(spm_unit, period, parameters)
