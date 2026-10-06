from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class ny_heap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP annualized income limit"
    unit = USD
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=37",
        "https://liheapch.acf.gov/docs/2026/state-plans/NY_Plan_2026.pdf#page=9",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/NY_BenefitMatrix_2026.docx",
        "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.otda.heap.eligibility
        size = max_(spm_unit("ny_heap_household_size", period), 1)
        state = spm_unit.household("state_code_str", period)
        base = parameters(period).gov.hhs.smi.amount[state]
        # ACF IM 2025-02 Attachment 4 floors the four-person 60% amount before
        # the federal size adjustment; this reproduces every published size
        # 1-13 limit.
        adjusted_smi = smi(size, state, period, parameters) / base
        monthly_smi = np.floor(
            adjusted_smi * np.floor(base * p.smi_rate) / MONTHS_IN_YEAR
        )
        monthly_fpg = np.floor(
            spm_unit("ny_heap_fpg", period) * p.fpg_rate / MONTHS_IN_YEAR
        )
        # Chapter 8 D.9(c) and the FY2026 plan control sizes 14+, where the
        # matrix's additional-person shortcut differs from the stated FPG rate.
        return max_(monthly_smi, monthly_fpg) * MONTHS_IN_YEAR
