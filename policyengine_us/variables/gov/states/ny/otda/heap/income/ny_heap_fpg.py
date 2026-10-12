from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ny_heap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP applicable federal poverty guideline"
    unit = USD
    defined_for = StateCode.NY
    reference = (
        # PDF pages 9, 10.
        "https://liheapch.acf.gov/docs/2026/state-plans/NY_Plan_2026.pdf#page=9",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/NY_BenefitMatrix_2026.docx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.otda.heap.eligibility
        size = max_(spm_unit("ny_heap_household_size", period), 1)
        state_group = spm_unit.household("state_group_str", period)
        return fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
