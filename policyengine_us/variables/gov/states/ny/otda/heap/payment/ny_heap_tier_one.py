from policyengine_us.model_api import *


class ny_heap_tier_one(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP Tier I status"
    defined_for = StateCode.NY
    reference = (
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
