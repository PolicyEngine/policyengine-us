from policyengine_us.model_api import *


class ny_heap_tier_one(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP Tier I status"
    defined_for = StateCode.NY
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/NY_Plan_2026.pdf#page=10",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/NY_BenefitMatrix_2026.docx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.otda.heap.payment
        threshold = (
            np.floor(
                spm_unit("ny_heap_fpg", period) * p.tier_one_fpg_rate / MONTHS_IN_YEAR
            )
            * MONTHS_IN_YEAR
        )
        return spm_unit("ny_heap_categorically_eligible", period) | (
            spm_unit("ny_heap_countable_income", period) <= threshold
        )
